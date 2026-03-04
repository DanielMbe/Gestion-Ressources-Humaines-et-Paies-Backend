from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from rest_framework import status
from datetime import date
from paies.models import Paie
from paies.serializers import PaieSerializer, PaieUpdateSerializer
from paies.services import generer_bulletin_pdf, calculer_salaire_net
from employes.models import Employe, RoleUtilisateur
from employes.serializers import EmployeUpdateSerializer
from decimal import Decimal
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class PaieViewSet(viewsets.ModelViewSet):
    serializer_class = PaieSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if not RoleUtilisateur.objects.filter(utilisateur=self.request.user, role=RoleUtilisateur.EMPLOYE).exists():
            PermissionDenied("Vous n'êtes pas un employé.")

        employe = Employe.objects.get(email=self.request.user.email)
        return Paie.objects.filter(employe_id=employe)

    def perform_create(self, serializer):
        try:
            employe = Employe.objects.get(administrateur=self.request.user, email=self.request.data.get("email"))
        except Employe.DoesNotExist:
            raise ValidationError("Employé pas liée a un administrateur.")

        salaire_base = Decimal(employe.salaire)
        serializer.save(employe_id=employe, salaire_base=salaire_base, salaire_net=salaire_base, date_paiement=date.today())
        calculer_salaire_net(salaire_base, employe)


class PaieView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) :
        employe = Employe.objects.get(email=request.query_params.get('email'), administrateur=self.request.user)
        return HttpResponse(generer_bulletin_pdf(employe=employe), content_type="application/pdf", headers={"Content-Disposition": "attachment; filename=bulletin_de_paie.pdf"})

    def put(self, request) :
        email = request.data.get("email")
        employe = get_object_or_404(Employe, email=email, administrateur=self.request.user)
        serializer = EmployeUpdateSerializer(employe, data={"statut": "Effectué"}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        paie = get_object_or_404(Paie, employe_id=employe)
        paie_serializer = PaieUpdateSerializer(paie, data={"date_paiement": date.today()}, partial=True)
        paie_serializer.is_valid(raise_exception=True)
        paie_serializer.save()

        return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)