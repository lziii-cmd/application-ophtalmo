"""
Vues API REST pour l'application ophtalmologique.
"""

from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.patients.models import Patient
from apps.patients.serializers import PatientSerializer
from apps.consultations.models import Consultation
from apps.consultations.serializers import ConsultationSerializer
from apps.agenda.models import RendezVous


class PatientListAPIView(generics.ListAPIView):
    """GET /api/patients/ - Liste paginée des patients."""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Patient.objects.all().order_by('nom', 'prenom')
        statut = self.request.query_params.get('statut')
        if statut:
            qs = qs.filter(statut=statut)
        q = self.request.query_params.get('q')
        if q:
            from django.db.models import Q
            qs = qs.filter(
                Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q)
            )
        return qs


class PatientDetailAPIView(generics.RetrieveAPIView):
    """GET /api/patients/{id}/ - Détail d'un patient."""
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Patient.objects.all()


class ConsultationListAPIView(generics.ListAPIView):
    """GET /api/consultations/ - Liste paginée des consultations."""
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Consultation.objects.select_related('patient', 'medecin').order_by('-date_heure')
        patient_id = self.request.query_params.get('patient')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def agenda_events_api(request):
    """GET /api/agenda/events/ - Événements pour FullCalendar."""
    rdvs = RendezVous.objects.select_related('patient', 'medecin').all()
    start = request.query_params.get('start')
    end = request.query_params.get('end')
    if start:
        rdvs = rdvs.filter(date_heure__gte=start)
    if end:
        rdvs = rdvs.filter(date_heure__lte=end)

    color_map = {
        'programme': '#0d6efd',
        'effectue': '#198754',
        'annule': '#dc3545',
        'non_presente': '#ffc107',
    }
    events = []
    for rdv in rdvs:
        events.append({
            'id': rdv.pk,
            'title': str(rdv.patient.nom_complet),
            'start': rdv.date_heure.isoformat(),
            'end': rdv.heure_fin.isoformat(),
            'backgroundColor': color_map.get(rdv.statut, '#6c757d'),
            'borderColor': color_map.get(rdv.statut, '#6c757d'),
            'extendedProps': {
                'statut': rdv.statut,
                'motif': rdv.motif,
                'medecin': rdv.medecin.get_full_name(),
            }
        })
    return Response(events)
