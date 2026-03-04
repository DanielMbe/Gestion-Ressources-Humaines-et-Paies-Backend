from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.db import transaction
from employes.models import RoleUtilisateur


Utilisateur = settings.AUTH_USER_MODEL

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def creer_nouvel_utilisateur(sender, instance, created, **kwargs):
    if created:
        def create_role():
            if not RoleUtilisateur.objects.filter(utilisateur=instance).exists():
                RoleUtilisateur.objects.create(utilisateur=instance, role=RoleUtilisateur.ADMINISTRATEUR)

        transaction.on_commit(create_role)