"""
URL configuration principale pour la clinique ophtalmologique.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('dashboard:index'), name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('patients/', include('apps.patients.urls', namespace='patients')),
    path('agenda/', include('apps.agenda.urls', namespace='agenda')),
    path('consultations/', include('apps.consultations.urls', namespace='consultations')),
    path('prescriptions/', include('apps.prescriptions.urls', namespace='prescriptions')),
    path('paiements/', include('apps.paiements.urls', namespace='paiements')),
    path('audit/', include('apps.audit.urls', namespace='audit')),
    path('sauvegarde/', include('apps.sauvegarde.urls', namespace='sauvegarde')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    path('api/', include('apps.api.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
