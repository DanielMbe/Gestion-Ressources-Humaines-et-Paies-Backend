from django.urls import path
from paies.views import PaieView, PaieViewSet

urlpatterns = [
    path("listpaies/", PaieViewSet.as_view({'get': 'list'}), name="list"),
    path("creerpaie/", PaieViewSet.as_view({'post': 'create'}), name="create"),
    path("validerpaie/", PaieView.as_view(), name="put"),
    path("salaire/", PaieView.as_view(), name="get"),
]