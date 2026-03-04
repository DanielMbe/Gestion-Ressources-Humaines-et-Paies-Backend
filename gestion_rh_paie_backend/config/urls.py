from django.contrib import admin
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("employes/", include("employes.urls")),
    path("paies/", include("paies.urls")),
    path("conges/", include("conges.urls")),
]
