from django.urls import path
from conges.views import ApprobationView, RejectionView, DemandeView, CongeViewSet

urlpatterns = [
    path("listconges/", CongeViewSet.as_view({'get': 'list'}), name="get"),
    path("creerconge/", CongeViewSet.as_view({'post': 'create'}), name="post"),
    path("approuverconge/", ApprobationView.as_view(), name="put"),
    path("rejeterconge/", RejectionView.as_view(), name="put"),
    path("demanderconge/", DemandeView.as_view(), name="put"),
]