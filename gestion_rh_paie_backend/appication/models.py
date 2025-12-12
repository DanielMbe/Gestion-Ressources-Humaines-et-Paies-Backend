from django.db import models
from django.utils import timezone
from decimal import Decimal, ROUND_HALF_UP
from xhtml2pdf import pisa
from io import BytesIO

class Employe(models.Model) :
    id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=128)
    prenom = models.CharField(max_length=256)
    email = models.CharField(max_length=128, unique=True)
    poste = models.CharField(max_length=128)
    departement = models.CharField(max_length=128)
    salaire = models.DecimalField(max_digits=9, decimal_places=2)
    solde_conge = models.SmallIntegerField()
    mot_de_passe = models.CharField(max_length=128)
    administrateur = models.CharField(max_length=128)
    disponibilite = models.CharField(max_length=64)
    statut = models.CharField(max_length=64)

    def nom_complet(self) :
        return self.nom + " " + self.prenom
    
    def set_solde_conge(self, jours) :
        self.solde_conge = jours


class Paie(models.Model) :
    id = models.AutoField(primary_key=True)
    employe_id = models.ForeignKey(Employe, on_delete=models.CASCADE)
    salaire_base = models.DecimalField(max_digits=9, decimal_places=2)
    salaire_net = models.DecimalField(max_digits=9, decimal_places=2)
    date_paiement = models.DateField(default=timezone.now)
    its = Decimal("0.0")
    cnps = Decimal("0.0")

    def calculer_salaire_net(self) :
        self.salaire_net = self.salaire_base - self.calculer_deduction()
        self.salaire_net = self.salaire_net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.salaire_net

    def calculer_deduction(self) :
        self.cnps = self.salaire_base * Decimal("0.063")
        self.cnps = self.cnps.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        different_ITS = {8000001 : Decimal("0.32"), 2400001 : Decimal("0.28"), 800001 : Decimal("0.24"), 240001 : Decimal("0.21"), 75001: Decimal("0.16"), 0 : Decimal("0.0")}

        for cle, valeur in sorted(different_ITS.items(), reverse=True) :
            if self.salaire_base >= cle :
                self.its = self.salaire_base * valeur
                self.its = self.its.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                break
        
        return self.cnps + self.its

    def generer_bulletin_pdf(self) :
        self.salaire_net = self.calculer_salaire_net()
        html = f""""
            <body>
                <h2>Bulletin de Salaire</h2>
                <div>Nom : {self.employe_id.nom}</div><div>Prenom : {self.employe_id.prenom}</div>
                <div>Poste : {self.employe_id.poste}</div><div>Departement : {self.employe_id.departement}</div>
                <div>Salaire de base : {self.salaire_base}</div><div>CNPS : {self.cnps}</div>
                <div>ITS : {self.its}</div><div>Salaire net : {self.salaire_net}</div>
            </body>
        """
        fichier = BytesIO()
        statut_pisa = pisa.CreatePDF(html, dest=fichier)

        if statut_pisa.err :
            return "Impossible de générer le bulletin de paie"
        return fichier.getvalue()


class Conge(models.Model) :
    id = models.AutoField(primary_key=True)
    employe_id = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=64)
    date_demande = models.DateField(default=timezone.now)

    def approuver(self) :
        self.statut = "Approuver"
        self.employe_id.solde_conge = self.date_fin - self.date_debut

    def rejeter(self) :
        self.statut = "Rejeter"
        self.employe_id.solde_conge = 0

    def mettre_ajour_statut(self, valeur) :
        self.statut = valeur