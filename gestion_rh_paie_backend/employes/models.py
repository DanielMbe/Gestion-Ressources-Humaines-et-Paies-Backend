from django.db import models
from django.conf import settings

Utilisateur = settings.AUTH_USER_MODEL

class Employe(models.Model) :
    nom = models.CharField(max_length=128)
    prenom = models.CharField(max_length=256)
    email = models.EmailField()
    poste = models.CharField(max_length=128)
    departement = models.CharField(max_length=128)
    salaire = models.DecimalField(max_digits=9, decimal_places=2)
    solde_conge = models.SmallIntegerField()
    mot_de_passe = models.CharField(max_length=128)
    administrateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    disponibilite = models.CharField(max_length=64)
    statut = models.CharField(max_length=64)

    class Meta:
        unique_together = ("administrateur", "email")

    def __str__(self):
        return f"{self.administrateur} - {self.email}"


class RoleUtilisateur(models.Model):
    ADMINISTRATEUR = "ADMINISTRATEUR"
    EMPLOYE = "EMPLOYE"
    CHOIX_ROLE = ((ADMINISTRATEUR, "ADMINISTRATEUR"), (EMPLOYE, "EMPLOYE"))

    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name="role")
    role = models.CharField(max_length=15, choices=CHOIX_ROLE)
    cree_a = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.utilisateur} - {self.role}"