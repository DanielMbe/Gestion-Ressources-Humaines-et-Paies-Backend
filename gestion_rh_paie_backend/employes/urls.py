from django.urls import path
from employes.views import LoginView, LogoutView, EmployeViewSet, EmployeView, RapportView

urlpatterns = [
    path("login/", LoginView.as_view(), name="post"),
    path("logout/", LogoutView.as_view(), name="post"),
    path("ajout/", EmployeViewSet.as_view({'post': 'create'}), name="create"),
    path("modifier/", EmployeView.as_view(), name="put"),
    path("stafftotal/", EmployeViewSet.as_view({'get': 'list'}), name="list"),
    path("rapportpdf/", RapportView.as_view(), name="get"),
]