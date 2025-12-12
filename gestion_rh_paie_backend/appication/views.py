from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from appication.models import Paie, Employe, Conge
from xhtml2pdf import pisa
from io import BytesIO
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
import random
from decimal import Decimal

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_bulletin_salaire(request) :
    employe = Employe.objects.get(id=int(request.GET.get("id")))
    paie = Paie.objects.select_related('employe_id').get(employe_id=employe)
    return HttpResponse(paie.generer_bulletin_pdf(), content_type="application/pdf", headers={"Content-Disposition": "attachment; filename=bulletin_de_paie.pdf"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def valider_paie(request) :
    employe = Employe.objects.get(id=request.data.get("id"))
    employe.statut = "Effectué"
    employe.save()

    paie = Paie.objects.select_related('employe_id').get(employe_id=employe)
    paie.date_paiement = timezone.now().date()
    paie.save()

    return JsonResponse({"message" : "Updated"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def generer_rapport_pdf(request) :
    admin = request.GET.get("loginID")
    salaires = Paie.objects.select_related('employe_id').filter(employe_id__administrateur=admin)
    html = "<h1>Rapport des Salaires</h1><ul>"
    for salaire in salaires:
        salaire.salaire_net = salaire.calculer_salaire_net()
        html += f""""
            <div>Nom : {salaire.employe_id.nom}</div><div>Prenom : {salaire.employe_id.prenom}</div>
            <div>Poste : {salaire.employe_id.poste}</div><div>Departement : {salaire.employe_id.departement}</div>
            <div>Salaire de base : {salaire.salaire_base}</div><div>CNPS : {salaire.cnps}</div>
            <div>ITS : {salaire.its}</div><div>Salaire net : {salaire.salaire_net}</div>
            <br/>
        """

    conges = Conge.objects.select_related("employe_id").filter(employe_id__administrateur=admin)
    html += "<h1>Rapport des Congés</h1><ul>"
    for conge in conges:
        html += f""""
            <div>Nom : {conge.employe_id.nom}</div><div>Prenom : {conge.employe_id.prenom}</div>
            <div>Poste : {conge.employe_id.poste}</div><div>Departement : {conge.employe_id.departement}</div>
            <div>Disponibilité : {conge.employe_id.disponibilite}</div><div>Date de demande de congé : {conge.date_demande}</div>
            <div>Jours de congé : {conge.employe_id.solde_conge}</div><div>Début de congé : {conge.date_debut}</div><div>Fin de congé : {conge.date_fin}</div>
            <br/>
        """

    fichier_pdf = BytesIO()
    pisa.CreatePDF(html, dest=fichier_pdf)
    return HttpResponse(fichier_pdf.getvalue(), content_type="application/pdf", headers={"Content-Disposition": "attachment; filename=rapport_RH.pdf"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approuver_conge(request) :
    employe = Employe.objects.get(id=request.data.get("id"))
    employe.disponibilite = "En Congé"
    employe.save()
    
    conge = Conge.objects.select_related("employe_id").get(employe_id=employe)
    conge.date_demande = timezone.now().date()
    conge.date_debut = timezone.now().date() + timedelta(days=7)
    conge.date_fin = conge.date_debut + timedelta(days=14)
    conge.approuver()
    conge.save()

    return JsonResponse({"message" : "Approuver"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rejeter_conge(request) :
    employe = Employe.objects.get(id=request.data.get("id"))
    employe.disponibilite = "En Service"
    employe.save()

    conge = Conge.objects.select_related("employe_id").get(employe_id=employe)
    conge.rejeter()
    conge.save()

    return JsonResponse({"message" : "Rejeter"})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def creer_employer(request) :
    lname = request.data.get("lname")
    fname = request.data.get("fname")
    mail = request.data.get("mail")
    job = request.data.get("job")
    dept = request.data.get("dept")
    earn = request.data.get("earn")
    admin = request.data.get("admin")
    list_disponibilite = ["En service", "En demande", "En demande"]
    list_statut = ["En attente", "Effectué"]

    nombre = Employe.objects.all().count()
    if nombre % 2 == 0:
        choix_statut = list_statut[1]
        choix_disponibilite = "En congé"
    else :
        choix_statut = list_statut[0]
        choix_disponibilite = random.choice(list_disponibilite)

    employer = Employe.objects.create(nom=lname, prenom=fname, email=mail, poste=job, departement=dept, salaire=Decimal(earn), solde_conge=0,
        mot_de_passe=lname + job, administrateur=admin, disponibilite=choix_disponibilite, statut=choix_statut)
    
    paie = Paie.objects.create(employe_id=employer, salaire_base=Decimal(earn), salaire_net=Decimal(earn))
    paie.calculer_salaire_net()

    conge = Conge.objects.create(employe_id=employer, statut=choix_statut)
    conge.mettre_ajour_statut("Rejeter")

    return JsonResponse(Employe.objects.order_by('-id').values().first())

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def modifier_employer(request) :
    employe = Employe.objects.get(id=int(request.data.get("cleId")))
    employe.email = request.data.get("mail")
    employe.poste = request.data.get("job")
    employe.departement = request.data.get("dept")
    employe.salaire = request.data.get("earn")
    employe.save()

    return JsonResponse({"message" : "Updated"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def liste_staff_employe(request) :
    admin = request.GET.get("loginID")
    reponse = JsonResponse(list(Employe.objects.filter(administrateur=admin).order_by('-id').values()), safe=False)
    #Employe.objects.all().delete()
    return reponse