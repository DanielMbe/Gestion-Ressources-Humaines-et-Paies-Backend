from employes.models import Employe
from conges.models import Conge
from paies.models import Paie
from paies.services import calculer_salaire_net
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse


def nom_complet(email) :
    employe = Employe.objects.get(email=email)
    return employe.nom + " " + employe.prenom


def set_solde_conge(email, jours) :
    employe = Employe.objects.get(email=email)
    employe.solde_conge = jours
    employe.save()


def generer_rapport_pdf(email) :
    admin = email
    salaires = Paie.objects.select_related("employe_id__administrateur").filter(employe_id__administrateur__email=admin)
    html = "<h1>Rapport des Salaires</h1><ul>"

    for salaire in salaires:
        salaire.salaire_net = calculer_salaire_net(salaire.salaire_base, salaire.employe_id)
        html += f""""
            <div>Nom : {salaire.employe_id.nom}</div><div>Prenom : {salaire.employe_id.prenom}</div>
            <div>Poste : {salaire.employe_id.poste}</div><div>Departement : {salaire.employe_id.departement}</div>
            <div>Salaire de base : {salaire.salaire_base}</div><div>CNPS : {salaire.cnps}</div>
            <div>ITS : {salaire.its}</div><div>Salaire net : {salaire.salaire_net}</div>
            <br/>
        """

    conges = Conge.objects.select_related("employe_id__administrateur").filter(employe_id__administrateur__email=admin)
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