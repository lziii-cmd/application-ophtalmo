"""
Vues pour la gestion des sauvegardes.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_POST
from pathlib import Path

from .models import Sauvegarde
from .utils import backup_database, restore_database, list_backup_files
from apps.accounts.decorators import admin_required
from apps.audit.utils import log_action


@login_required
@admin_required
def sauvegarde_dashboard_view(request):
    """Tableau de bord des sauvegardes (admin seulement)."""
    sauvegardes = Sauvegarde.objects.all().order_by('-date_heure')[:50]
    fichiers = list_backup_files()

    # Dernière sauvegarde réussie
    derniere_sauvegarde = Sauvegarde.objects.filter(statut='reussie').first()

    return render(request, 'sauvegarde/dashboard.html', {
        'sauvegardes': sauvegardes,
        'fichiers': fichiers,
        'derniere_sauvegarde': derniere_sauvegarde,
    })


@login_required
@admin_required
@require_POST
def sauvegarde_create_view(request):
    """Déclenche une sauvegarde manuelle."""
    force_type = request.POST.get('type', None)
    if force_type not in ['complete', 'incrementale', None]:
        force_type = None

    sauvegarde = backup_database(user=request.user, force_type=force_type)

    if sauvegarde.statut == 'reussie':
        messages.success(
            request,
            f"Sauvegarde {sauvegarde.get_type_sauvegarde_display()} créée avec succès: "
            f"{sauvegarde.taille_lisible}, {sauvegarde.nombre_enregistrements} enregistrements."
        )
    else:
        messages.error(
            request,
            f"Échec de la sauvegarde: {sauvegarde.message_erreur}"
        )

    return redirect('sauvegarde:dashboard')


@login_required
@admin_required
def sauvegarde_restore_confirm_view(request, pk):
    """Page de confirmation de restauration (double confirmation - R17)."""
    sauvegarde = get_object_or_404(Sauvegarde, pk=pk)

    return render(request, 'sauvegarde/restore_confirm.html', {
        'sauvegarde': sauvegarde,
    })


@login_required
@admin_required
@require_POST
def sauvegarde_restore_view(request, pk):
    """
    Exécute la restauration après double confirmation.
    R17: Seul admin peut restaurer, double confirmation.
    R16: Sauvegarde auto avant restauration.
    """
    sauvegarde = get_object_or_404(Sauvegarde, pk=pk)

    # Vérification de la double confirmation
    confirmation1 = request.POST.get('confirm1') == 'on'
    confirmation2 = request.POST.get('confirm2') == 'on'
    password = request.POST.get('admin_password', '')

    if not confirmation1 or not confirmation2:
        messages.error(request, "Vous devez cocher les deux cases de confirmation.")
        return redirect('sauvegarde:restore_confirm', pk=pk)

    # Vérification du mot de passe admin
    if not request.user.check_password(password):
        messages.error(request, "Mot de passe administrateur incorrect.")
        log_action(
            user=request.user,
            action='RESTORE',
            entity='Sauvegarde',
            entity_id=str(pk),
            after={'statut': 'tentative_refusee', 'raison': 'mot_de_passe_incorrect'},
            request=request
        )
        return redirect('sauvegarde:restore_confirm', pk=pk)

    # Exécution de la restauration
    result = restore_database(backup_pk=pk, user=request.user)

    if result['success']:
        messages.success(request, result['message'])
        messages.warning(
            request,
            "La base de données a été restaurée. Veuillez vous reconnecter."
        )
        from django.contrib.auth import logout
        logout(request)
        return redirect('accounts:login')
    else:
        messages.error(request, f"Échec de la restauration: {result['message']}")
        return redirect('sauvegarde:dashboard')


@login_required
@admin_required
def sauvegarde_download_view(request, pk):
    """Téléchargement d'un fichier de sauvegarde (chiffré)."""
    sauvegarde = get_object_or_404(Sauvegarde, pk=pk)
    backup_path = Path(sauvegarde.fichier_path)

    if not backup_path.exists():
        messages.error(request, "Fichier de sauvegarde introuvable.")
        return redirect('sauvegarde:dashboard')

    log_action(
        user=request.user,
        action='READ',
        entity='Sauvegarde',
        entity_id=str(pk),
        after={'action': 'download'},
        request=request
    )

    response = FileResponse(
        open(backup_path, 'rb'),
        content_type='application/octet-stream'
    )
    response['Content-Disposition'] = f'attachment; filename="{backup_path.name}"'
    return response
