"""
Vues pour la gestion des comptes utilisateurs.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import CustomUser
from .forms import LoginForm, UserCreateForm, UserEditForm, PasswordChangeCustomForm
from .decorators import admin_required, role_required
from apps.audit.utils import log_action


def login_view(request):
    """Vue de connexion avec gestion du verrouillage de compte."""
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        username = request.POST.get('username', '')

        # Vérification du verrouillage avant authentification
        try:
            user_obj = CustomUser.objects.get(username=username)
            if user_obj.is_locked:
                messages.error(
                    request,
                    f"Ce compte est verrouillé jusqu'au "
                    f"{user_obj.locked_until.strftime('%d/%m/%Y à %H:%M')}. "
                    f"Contactez l'administrateur."
                )
                log_action(
                    user=None,
                    action='LOGIN',
                    entity='CustomUser',
                    entity_id=str(user_obj.pk),
                    after={'status': 'blocked', 'username': username},
                    request=request
                )
                return render(request, 'accounts/login.html', {'form': LoginForm()})
        except CustomUser.DoesNotExist:
            pass

        if form.is_valid():
            user = form.get_user()
            user.reset_failed_login()
            login(request, user)
            request.session['last_activity'] = timezone.now().isoformat()
            log_action(
                user=user,
                action='LOGIN',
                entity='CustomUser',
                entity_id=str(user.pk),
                after={'status': 'success', 'username': user.username},
                request=request
            )
            messages.success(request, f"Bienvenue, {user.get_full_name() or user.username} !")
            next_url = request.GET.get('next', 'dashboard:index')
            return redirect(next_url)
        else:
            # Incrémenter le compteur d'échecs
            try:
                user_obj = CustomUser.objects.get(username=username)
                user_obj.increment_failed_login()
                remaining = max(0, 5 - user_obj.failed_login_count)
                if remaining > 0:
                    messages.error(
                        request,
                        f"Identifiants incorrects. {remaining} tentative(s) restante(s) avant verrouillage."
                    )
                else:
                    messages.error(
                        request,
                        "Compte verrouillé suite à trop de tentatives. Contactez l'administrateur."
                    )
                log_action(
                    user=None,
                    action='LOGIN',
                    entity='CustomUser',
                    entity_id=str(user_obj.pk),
                    after={'status': 'failed', 'attempts': user_obj.failed_login_count},
                    request=request
                )
            except CustomUser.DoesNotExist:
                messages.error(request, "Identifiants incorrects.")
    else:
        form = LoginForm()

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Vue de déconnexion."""
    user = request.user
    log_action(
        user=user,
        action='LOGIN',
        entity='CustomUser',
        entity_id=str(user.pk),
        after={'status': 'logout'},
        request=request
    )
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Vue du profil utilisateur."""
    if request.method == 'POST':
        form = PasswordChangeCustomForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            log_action(
                user=request.user,
                action='UPDATE',
                entity='CustomUser',
                entity_id=str(request.user.pk),
                after={'action': 'password_changed'},
                request=request
            )
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Erreur lors du changement de mot de passe.")
    else:
        form = PasswordChangeCustomForm(request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'user': request.user})


@login_required
@admin_required
def users_list_view(request):
    """Liste des utilisateurs (admin seulement)."""
    users = CustomUser.objects.all().order_by('last_name', 'first_name')
    return render(request, 'accounts/users_list.html', {'users': users})


@login_required
@admin_required
def user_create_view(request):
    """Création d'un utilisateur (admin seulement)."""
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_action(
                user=request.user,
                action='CREATE',
                entity='CustomUser',
                entity_id=str(user.pk),
                after={
                    'username': user.username,
                    'role': user.role,
                    'full_name': user.get_full_name()
                },
                request=request
            )
            messages.success(request, f"Utilisateur '{user.get_full_name()}' créé avec succès.")
            return redirect('accounts:users_list')
        else:
            messages.error(request, "Erreur lors de la création de l'utilisateur.")
    else:
        form = UserCreateForm()

    return render(request, 'accounts/user_form.html', {'form': form, 'action': 'Créer'})


@login_required
@admin_required
def user_edit_view(request, pk):
    """Modification d'un utilisateur (admin seulement)."""
    user = get_object_or_404(CustomUser, pk=pk)
    before_data = {
        'username': user.username,
        'role': user.role,
        'is_active': user.is_active
    }

    if request.method == 'POST':
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
            log_action(
                user=request.user,
                action='UPDATE',
                entity='CustomUser',
                entity_id=str(user.pk),
                before=before_data,
                after={
                    'username': user.username,
                    'role': user.role,
                    'is_active': user.is_active
                },
                request=request
            )
            messages.success(request, f"Utilisateur '{user.get_full_name()}' modifié avec succès.")
            return redirect('accounts:users_list')
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = UserEditForm(instance=user)

    return render(request, 'accounts/user_form.html', {
        'form': form,
        'action': 'Modifier',
        'edit_user': user
    })


@login_required
@admin_required
def user_unlock_view(request, pk):
    """Déverrouillage d'un compte utilisateur (admin seulement)."""
    user = get_object_or_404(CustomUser, pk=pk)
    user.unlock_account()
    log_action(
        user=request.user,
        action='UPDATE',
        entity='CustomUser',
        entity_id=str(user.pk),
        after={'action': 'account_unlocked', 'username': user.username},
        request=request
    )
    messages.success(request, f"Compte de '{user.get_full_name()}' déverrouillé.")
    return redirect('accounts:users_list')


@login_required
@admin_required
def user_toggle_active_view(request, pk):
    """Activer/désactiver un compte utilisateur."""
    user = get_object_or_404(CustomUser, pk=pk)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('accounts:users_list')

    before_active = user.is_active
    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    action_label = "activé" if user.is_active else "désactivé"
    log_action(
        user=request.user,
        action='UPDATE',
        entity='CustomUser',
        entity_id=str(user.pk),
        before={'is_active': before_active},
        after={'is_active': user.is_active},
        request=request
    )
    messages.success(request, f"Compte de '{user.get_full_name()}' {action_label}.")
    return redirect('accounts:users_list')
