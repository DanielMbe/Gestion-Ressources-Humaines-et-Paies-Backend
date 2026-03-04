from django.db import models
from datetime import date
from employes.models import Employe

class Conge(models.Model) :
    employe_id = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date_debut = models.DateField(default=date.today())
    date_fin = models.DateField(default=date.today())
    statut = models.CharField(max_length=64)
    date_demande = models.DateField(default=date.today())

    def __str__(self):
        return f"{self.employe_id.email}-{self.date_debut}"
