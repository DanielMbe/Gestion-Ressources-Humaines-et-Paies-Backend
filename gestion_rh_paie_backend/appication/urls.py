from django.urls import path
from rest_framework_simplejwt.views import (TokenObtainPairView, TokenRefreshView)
from . import views

urlpatterns = [
    path('signin/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("salaire/", views.get_bulletin_salaire, name="get_bulletin_salaire"),
    path("rapportpdf/", views.generer_rapport_pdf, name="generer_rapport_pdf"),
    path("ajout/", views.creer_employer, name="creer_employer"),
    path("approuverconge/", views.approuver_conge, name="approuver_conge"),
    path("rejeterconge/", views.rejeter_conge, name="rejeter_conge"),
    path("stafftotal/", views.liste_staff_employe, name="liste_staff_employe"),
    path("modifier/", views.modifier_employer, name="modifier_employer"),
    path("validerpaie/", views.valider_paie, name="valider_paie"),
]