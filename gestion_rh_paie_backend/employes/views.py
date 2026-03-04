from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404
from employes.models import (Employe, RoleUtilisateur)
from employes.serializers import EmployeSerializer, EmployeUpdateSerializer
from employes.services import generer_rapport_pdf
from utilisateurs.models import Utilisateur

class EmployeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        #if not RoleUtilisateur.objects.filter(utilisateur=self.request.user, role=RoleUtilisateur.ADMINISTRATEUR).exists():
        #    raise PermissionDenied("Vous n'êtes pas administrateur.")
        '''Employe.objects.all().delete()
        from conges.models import Conge
        Conge.objects.all().delete()'''
        return Employe.objects.filter(administrateur=self.request.user).order_by('-id')
    
    def perform_create(self, serializer):
        #if not RoleUtilisateur.objects.filter(utilisateur=self.request.user, role=RoleUtilisateur.ADMINISTRATEUR).exists():
            #raise PermissionDenied("Vous n'êtes pas administrateur.")

        serializer.save(solde_conge=0, mot_de_passe=self.request.data.get('poste'), disponibilite="En service",
                                   statut="En attente", administrateur=self.request.user)

        utilisateur = Utilisateur.objects.create_superuser(email=self.request.data.get('email'), username=self.request.data.get('email'), password=self.request.data.get('poste'))
        RoleUtilisateur.objects.create(utilisateur=utilisateur, role=RoleUtilisateur.EMPLOYE)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        utilisateur = authenticate(email=request.data.get('email'), password=request.data.get('mot_de_passe'))

        if not utilisateur:
            return Response({"detail": "Identifiant ou mot de passe incorrecte"}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(utilisateur)
        
        role = "Hacker"
        if RoleUtilisateur.objects.filter(utilisateur=utilisateur, role=RoleUtilisateur.EMPLOYE).exists():
            role = "Employe"
        if RoleUtilisateur.objects.filter(utilisateur=utilisateur, role=RoleUtilisateur.ADMINISTRATEUR).exists():
            role = "Admin"
            
        return Response({"access": str(refresh.access_token), "refresh": str(refresh), "role" : str(role)})
    

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        logout(request)
        return Response({"message": "Logged out"})
    

class EmployeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        email = request.data.get("email")
        employe = get_object_or_404(Employe, email=email, administrateur=self.request.user)

        serializer = EmployeUpdateSerializer(employe, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"message": "Updated successfully"}, status=status.HTTP_200_OK)


class RapportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request) :
        return generer_rapport_pdf(self.request.user.email)