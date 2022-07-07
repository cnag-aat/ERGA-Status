from django.urls import path

from . import views
from status.views import TargetSpeciesListView
from status.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
]
