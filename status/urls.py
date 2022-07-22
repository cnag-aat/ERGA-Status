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
    path("species/?scientific_name=<scientific_name>", views.species_detail, name="species_detail"),
    path("assemblies/", AssemblyListView.as_view(), name="assembly_list"),
    path("projects/", AssemblyProjectListView.as_view(), name="assembly_project_list"),
    path("projects/?species=<scientific_name>", AssemblyProjectListView.as_view(), name="assembly_project_list"),path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("collection_team/<int:pk>/", views.collection_team_detail, name="collection_team_detail"),
    path("sequencing_team/<int:pk>/", views.sequencing_team_detail, name="sequencing_team_detail"),
    path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("curation_team/<int:pk>/", views.curation_team_detail, name="curation_team_detail"),
    path("annotation_team/<int:pk>/", views.annotation_team_detail, name="annotation_team_detail"),
    path("submission_team/<int:pk>/", views.submission_team_detail, name="submission_team_detail"),

]
