from django.db import models
from datetime import date
from employes.models import Employe
from decimal import Decimal

class Paie(models.Model) :
    employe_id = models.ForeignKey(Employe, on_delete=models.CASCADE)
    salaire_base = models.DecimalField(max_digits=9, decimal_places=2)
    salaire_net = models.DecimalField(max_digits=9, decimal_places=2)
    date_paiement = models.DateField(default=date.today())
    its = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0.00"))
    cnps = models.DecimalField(max_digits=9, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return f"{self.employe_id.email}-{self.salaire_base}"