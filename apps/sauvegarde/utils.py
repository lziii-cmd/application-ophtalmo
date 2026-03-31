"""
Utilitaires pour la sauvegarde et restauration de la base de données.
Chiffrement AES-256 avec PyCryptodome.
Règles: R15, R16, R17, R18
"""

import os
import shutil
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger('apps.sauvegarde')

BACKUP_DIR = Path(settings.BACKUP_DIR)
DB_PATH = Path(settings.DATABASES['default']['NAME'])

AES_BLOCK_SIZE = 16


def get_encryption_key():
    """
    Dérive une clé AES-256 (32 bytes) depuis la configuration.
    Utilise SHA-256 pour garantir exactement 32 bytes.
    """
    raw_key = settings.BACKUP_ENCRYPTION_KEY
    if isinstance(raw_key, str):
        raw_key = raw_key.encode('utf-8')
    return hashlib.sha256(raw_key).digest()


def _get_crypto():
    """Import paresseux de PyCryptodome pour éviter l'erreur au démarrage."""
    try:
        from Crypto.Cipher import AES
        from Crypto.Random import get_random_bytes
        from Crypto.Util.Padding import pad, unpad
        return AES, get_random_bytes, pad, unpad
    except ImportError:
        raise ImportError(
            "Le module 'pycryptodome' est requis pour la sauvegarde chiffrée. "
            "Installez-le avec : pip install pycryptodome"
        )


def encrypt_file(source_path, dest_path):
    """
    Chiffre un fichier avec AES-256 CBC (R18).
    Format du fichier chiffré: [16 bytes IV][données chiffrées]
    Retourne la taille du fichier chiffré.
    """
    AES, get_random_bytes, pad, unpad = _get_crypto()
    key = get_encryption_key()
    iv = get_random_bytes(AES_BLOCK_SIZE)
    cipher = AES.new(key, AES.MODE_CBC, iv)

    with open(source_path, 'rb') as f:
        plaintext = f.read()

    ciphertext = cipher.encrypt(pad(plaintext, AES_BLOCK_SIZE))

    with open(dest_path, 'wb') as f:
        f.write(iv)
        f.write(ciphertext)

    return Path(dest_path).stat().st_size


def decrypt_file(source_path, dest_path):
    """
    Déchiffre un fichier chiffré avec AES-256 CBC.
    """
    AES, get_random_bytes, pad, unpad = _get_crypto()
    key = get_encryption_key()

    with open(source_path, 'rb') as f:
        iv = f.read(AES_BLOCK_SIZE)
        ciphertext = f.read()

    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES_BLOCK_SIZE)

    with open(dest_path, 'wb') as f:
        f.write(plaintext)


def count_records():
    """Compte le nombre total d'enregistrements dans la base SQLite."""
    total = 0
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                if not table.startswith('sqlite_'):
                    try:
                        cursor.execute(f'SELECT COUNT(*) FROM "{table}"')
                        total += cursor.fetchone()[0]
                    except Exception:
                        pass
    except Exception as e:
        logger.error(f"Erreur comptage enregistrements: {e}")
    return total


def is_first_backup_of_day():
    """
    Vérifie si c'est la première sauvegarde réussie du jour (R15).
    """
    from .models import Sauvegarde
    today = timezone.now().date()
    return not Sauvegarde.objects.filter(
        date_heure__date=today,
        statut='reussie'
    ).exists()


def backup_database(user=None, force_type=None):
    """
    Sauvegarde la base de données avec chiffrement AES-256.

    R15: Première sauvegarde du jour = complète, suivantes = incrémentales.
    R18: Fichiers chiffrés AES-256.

    Args:
        user: Utilisateur déclenchant la sauvegarde
        force_type: Forcer 'complete' ou 'incrementale' (sinon auto selon R15)

    Returns:
        Instance de Sauvegarde avec statut mis à jour
    """
    from .models import Sauvegarde

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    # Détermination automatique du type (R15)
    if force_type in ('complete', 'incrementale'):
        backup_type = force_type
    elif is_first_backup_of_day():
        backup_type = 'complete'
    else:
        backup_type = 'incrementale'

    # Génération du nom de fichier
    now = timezone.now()
    type_suffix = 'complete' if backup_type == 'complete' else 'incrementale'
    filename = f"sauvegarde_{now.strftime('%Y-%m-%d_%Hh%M')}_{type_suffix}.bak"
    backup_path = BACKUP_DIR / filename
    temp_path = BACKUP_DIR / f"temp_{now.strftime('%Y%m%d_%H%M%S')}.db"

    # Créer l'entrée en base (statut: en_cours)
    sauvegarde = Sauvegarde(
        date_heure=now,
        type_sauvegarde=backup_type,
        fichier_path=str(backup_path),
        statut='en_cours',
        created_by=user,
    )
    # Bypass le modèle immuable (Sauvegarde n'est pas AuditLog)
    sauvegarde.save()

    try:
        if not DB_PATH.exists():
            raise FileNotFoundError(f"Base de données introuvable: {DB_PATH}")

        # Fermeture propre des connexions Django avant copie
        from django.db import connections
        for conn_name in connections:
            try:
                connections[conn_name].close()
            except Exception:
                pass

        # Copie de la base SQLite vers fichier temporaire
        shutil.copy2(str(DB_PATH), str(temp_path))

        # Chiffrement AES-256 (R18)
        taille = encrypt_file(temp_path, backup_path)

        # Suppression du fichier temporaire non chiffré
        if temp_path.exists():
            temp_path.unlink()

        # Reconnecter et compter les enregistrements
        from django.db import connection
        connection.ensure_connection()
        nb_records = count_records()

        # Mise à jour du statut de la sauvegarde
        Sauvegarde.objects.filter(pk=sauvegarde.pk).update(
            taille_octets=taille,
            statut='reussie',
            nombre_enregistrements=nb_records,
        )
        sauvegarde.taille_octets = taille
        sauvegarde.statut = 'reussie'
        sauvegarde.nombre_enregistrements = nb_records

        # Audit log
        from apps.audit.utils import log_action
        log_action(
            user=user,
            action='BACKUP',
            entity='Sauvegarde',
            entity_id=str(sauvegarde.pk),
            after={
                'type': backup_type,
                'fichier': filename,
                'taille': taille,
                'nb_enregistrements': nb_records,
                'statut': 'reussie',
            }
        )

        logger.info(f"Sauvegarde réussie: {filename} ({taille} octets, {nb_records} enregistrements)")

    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde: {e}", exc_info=True)

        # Nettoyage des fichiers temporaires
        for f in [temp_path, backup_path]:
            try:
                if f.exists():
                    f.unlink()
            except Exception:
                pass

        # Mise à jour statut échec
        try:
            from django.db import connection
            connection.ensure_connection()
            Sauvegarde.objects.filter(pk=sauvegarde.pk).update(
                statut='echec',
                message_erreur=str(e)[:500],
            )
        except Exception:
            pass

        sauvegarde.statut = 'echec'
        sauvegarde.message_erreur = str(e)

        from apps.audit.utils import log_action
        try:
            log_action(
                user=user,
                action='BACKUP',
                entity='Sauvegarde',
                entity_id=str(sauvegarde.pk),
                after={'statut': 'echec', 'erreur': str(e)}
            )
        except Exception:
            pass

    return sauvegarde


def restore_database(backup_pk, user=None):
    """
    Restaure la base de données depuis une sauvegarde chiffrée.

    R16: Sauvegarde automatique avant toute restauration.
    R17: Seul l'admin peut restaurer (vérifié dans la vue).

    Args:
        backup_pk: PK de la sauvegarde à restaurer
        user: Utilisateur déclenchant la restauration

    Returns:
        dict avec 'success' (bool) et 'message' (str)
    """
    from .models import Sauvegarde
    from apps.audit.utils import log_action

    try:
        sauvegarde = Sauvegarde.objects.get(pk=backup_pk)
    except Sauvegarde.DoesNotExist:
        return {'success': False, 'message': f"Sauvegarde #{backup_pk} introuvable."}

    backup_path = Path(sauvegarde.fichier_path)
    if not backup_path.exists():
        return {'success': False, 'message': f"Fichier de sauvegarde introuvable: {backup_path}"}

    # R16: Sauvegarde automatique avant restauration
    logger.info("R16: Création d'une sauvegarde automatique pré-restauration...")
    pre_backup = backup_database(user=user, force_type='complete')
    if pre_backup.statut != 'reussie':
        return {
            'success': False,
            'message': "Impossible de créer la sauvegarde pré-restauration. Restauration annulée par sécurité."
        }

    # Fermeture des connexions Django
    from django.db import connections
    for conn_name in connections:
        try:
            connections[conn_name].close()
        except Exception:
            pass

    temp_restore_path = BACKUP_DIR / f"restore_temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

    try:
        decrypt_file(backup_path, temp_restore_path)
    except Exception as e:
        if temp_restore_path.exists():
            temp_restore_path.unlink()
        return {'success': False, 'message': f"Erreur de déchiffrement du fichier: {e}"}

    try:
        # Copie de sécurité de la DB actuelle
        db_safety_path = DB_PATH.parent / f"ophtalmo_pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(str(DB_PATH), str(db_safety_path))

        # Remplacement de la base de données
        shutil.copy2(str(temp_restore_path), str(DB_PATH))

        if temp_restore_path.exists():
            temp_restore_path.unlink()

        log_action(
            user=user,
            action='RESTORE',
            entity='Sauvegarde',
            entity_id=str(backup_pk),
            after={
                'statut': 'reussie',
                'source': str(backup_path),
                'pre_restore_backup_id': str(pre_backup.pk),
            }
        )

        logger.info(f"Restauration réussie depuis: {backup_path}")
        return {
            'success': True,
            'message': (
                f"Base de données restaurée avec succès depuis la sauvegarde "
                f"du {sauvegarde.date_heure.strftime('%d/%m/%Y à %H:%M')}. "
                f"Sauvegarde pré-restauration: #{pre_backup.pk}."
            )
        }

    except Exception as e:
        if temp_restore_path.exists():
            temp_restore_path.unlink()
        log_action(
            user=user,
            action='RESTORE',
            entity='Sauvegarde',
            entity_id=str(backup_pk),
            after={'statut': 'echec', 'erreur': str(e)}
        )
        logger.error(f"Erreur restauration: {e}", exc_info=True)
        return {'success': False, 'message': f"Erreur lors de la restauration: {e}"}


def list_backup_files():
    """Liste les fichiers .bak présents dans le répertoire de sauvegarde."""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    files = []
    for f in sorted(BACKUP_DIR.glob('sauvegarde_*.bak'), key=lambda x: x.stat().st_mtime, reverse=True):
        files.append({
            'name': f.name,
            'path': str(f),
            'size': f.stat().st_size,
            'size_hr': _human_size(f.stat().st_size),
            'modified': datetime.fromtimestamp(f.stat().st_mtime),
        })
    return files


def _human_size(size_bytes):
    """Convertit une taille en octets vers un format lisible."""
    if size_bytes < 1024:
        return f"{size_bytes} o"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} Ko"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024**2:.1f} Mo"
    return f"{size_bytes / 1024**3:.1f} Go"
