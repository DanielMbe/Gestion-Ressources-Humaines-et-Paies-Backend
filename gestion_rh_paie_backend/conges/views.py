from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError, PermissionDenied
from django.http import JsonResponse
from datetime import timedelta, date
from conges.models import Conge
from conges.serializers import CongeSerializer, CongeUpdateSerializer
from employes.models import Employe, RoleUtilisateur
from employes.serializers import EmployeUpdateSerializer
from django.shortcuts import get_object_or_404


class CongeViewSet(viewsets.ModelViewSet):
    serializer_class = CongeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not RoleUtilisateur.objects.filter(utilisateur=self.request.user, role=RoleUtilisateur.EMPLOYE).exists():
            PermissionDenied("Vous n'êtes pas un employé.")

        employe = Employe.objects.get(email=self.request.user.email)
        return Conge.objects.filter(employe_id=employe)

    def perform_create(self, serializer):
        try:
            employe = Employe.objects.get(administrateur=self.request.user, email=self.request.data.get("email"))
        except Employe.DoesNotExist:
            raise ValidationError("Employé pas liée a un administrateur.")
        
        serializer.save(employe_id=employe, statut="Rejeter", date_debut=date.today(), date_fin=date.today(), date_demande=date.today())


class ApprobationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        email = request.data.get("email")
        
        employe = get_object_or_404(Employe, email=email, administrateur=self.request.user)
        serializer = EmployeUpdateSerializer(employe, data={"disponibilite": "En congé"}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        conge = get_object_or_404(Conge, employe_id=employe)
        conge_serializer = CongeUpdateSerializer(conge, data={
            "date_demande": date.today(),
            "date_debut": date.today() + timedelta(days=7),
            "date_fin": date.today() + timedelta(days=21),
            "statut": "Approuver",
            }, partial=True)
        conge_serializer.is_valid(raise_exception=True)
        conge_serializer.save()

        return JsonResponse({"message" : "Approuver"})

class RejectionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        email = request.data.get("email")
        employe = get_object_or_404(Employe, email=email, administrateur=self.request.user)
        serializer = EmployeUpdateSerializer(employe, data={"disponibilite": "En service"}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        conge = get_object_or_404(Conge, employe_id=employe)
        conge_serializer = CongeUpdateSerializer(conge, data={"statut": "Rejeter"}, partial=True)
        conge_serializer.is_valid(raise_exception=True)
        conge_serializer.save()

        return JsonResponse({"message" : "Rejeter"})
    

class DemandeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        employe = get_object_or_404(Employe, email=self.request.user.email)
        serializer = EmployeUpdateSerializer(employe, data={"disponibilite": "En demande"}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        conge = get_object_or_404(Conge, employe_id=employe)
        conge_serializer = CongeUpdateSerializer(conge, data={"statut": "Demander"}, partial=True)
        conge_serializer.is_valid(raise_exception=True)
        conge_serializer.save()

        return JsonResponse({"message" : "Demander"})