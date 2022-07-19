from django.urls import path

from . import views
from status.views import TargetSpeciesListView
from status.views import AssemblyListView
from status.views import AssemblyProjectListView
from status.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
    path("species/<int:pk>/", views.species_detail, name="species_detail"),
    path("assemblies/", AssemblyListView.as_view(), name="assembly_list"),
    path("projects/", AssemblyProjectListView.as_view(), name="assembly_project_list"),
]
