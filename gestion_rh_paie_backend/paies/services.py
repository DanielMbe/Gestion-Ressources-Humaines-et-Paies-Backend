from decimal import Decimal, ROUND_HALF_UP
from xhtml2pdf import pisa
from io import BytesIO
from django.utils import timezone
from paies.models import Paie
from paies.serializers import PaieUpdateSerializer


def calculer_salaire_net(salaire_base, employe) :
    salaire_net = Decimal(salaire_base - calculer_deduction(employe))
    salaire_net = salaire_net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    paie = Paie.objects.get(employe_id=employe)
    paie_serializer = PaieUpdateSerializer(paie, data={"salaire_net" : salaire_net}, partial=True)
    paie_serializer.is_valid(raise_exception=True)
    paie_serializer.save()

    return salaire_net

def calculer_deduction(employe) :
    paie = Paie.objects.get(employe_id=employe)
    cnps = Decimal(paie.salaire_base * Decimal("0.063"))
    cnps = cnps.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    its = Decimal(0.00)
    different_ITS = {8000001 : Decimal("0.32"), 2400001 : Decimal("0.28"), 800001 : Decimal("0.24"), 240001 : Decimal("0.21"), 75001: Decimal("0.16"), 0 : Decimal("0.0")}

    for cle, valeur in sorted(different_ITS.items(), reverse=True) :
        if paie.salaire_base >= cle :
            its = paie.salaire_base * valeur
            its = its.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            break

    paie_serializer = PaieUpdateSerializer(paie, data={"its" : its, "cnps" : cnps}, partial=True)
    paie_serializer.is_valid(raise_exception=True)
    paie_serializer.save()
    
    return cnps + its

def generer_bulletin_pdf(employe) :
    paie = Paie.objects.get(employe_id=employe)
    paie.salaire_net = calculer_salaire_net(paie.salaire_base, employe)
    html = f""""
        <body>
            <h2>Bulletin de Salaire</h2>
            <div>Nom : {paie.employe_id.nom}</div><div>Prenom : {paie.employe_id.prenom}</div>
            <div>Poste : {paie.employe_id.poste}</div><div>Departement : {paie.employe_id.departement}</div>
            <div>Salaire de base : {paie.salaire_base}</div><div>CNPS : {paie.cnps}</div>
            <div>ITS : {paie.its}</div><div>Salaire net : {paie.salaire_net}</div>
        </body>
    """
    fichier = BytesIO()
    statut_pisa = pisa.CreatePDF(html, dest=fichier)

    if statut_pisa.err :
        return "Impossible de générer le bulletin de paie"
    return fichier.getvalue()