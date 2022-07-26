from django.urls import path
from django.conf.urls import url

from . import views
from status.views import TargetSpeciesListView
from status.views import AssemblyListView
from status.views import SampleCollectionListView
from status.views import SequencingListView
from status.views import ReadsListView
from status.views import AssemblyProjectListView
from status.views import CurationListView
from status.views import AnnotationListView
from status.views import SubmissionListView
from status.views import HomeView
from status.views import OverView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("overview/", OverView.as_view(), name="overview"),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
    path("species/<int:pk>/", views.species_detail, name="species_detail"),
    path("species/?scientific_name=<scientific_name>", views.species_detail, name="species_detail"),
    path("assemblies/", AssemblyListView.as_view(), name="assembly_list"),
    path("projects/", AssemblyProjectListView.as_view(), name="assembly_project_list"),
    path("projects/?species=<scientific_name>", AssemblyProjectListView.as_view(), name="assembly_project_list"),
    path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("collection_team/<int:pk>/", views.collection_team_detail, name="collection_team_detail"),
    path("sequencing_team/<int:pk>/", views.sequencing_team_detail, name="sequencing_team_detail"),
    path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("curation_team/<int:pk>/", views.curation_team_detail, name="curation_team_detail"),
    path("annotation_team/<int:pk>/", views.annotation_team_detail, name="annotation_team_detail"),
    path("submission_team/<int:pk>/", views.submission_team_detail, name="submission_team_detail"),
    url('collection/?species=<species_id>', SampleCollectionListView.as_view(), kwargs=None, name="collection_list"),
    path("sequencing/?species=<scientific_name>", SequencingListView.as_view(), name="sequencing_list"),
    path("curation/?species=<scientific_name>", CurationListView.as_view(), name="curation_list"),
    path("annotation/?species=<scientific_name>", AnnotationListView.as_view(), name="annotation_list"),
    path("submission/?species=<scientific_name>", SubmissionListView.as_view(), name="submission_list"),
    path("collection/", SampleCollectionListView.as_view(), name="collection_list"),
    path("sequencing/", SequencingListView.as_view(), name="sequencing_list"),
    path("reads/", ReadsListView.as_view(), name="reads_list"),
    path("curation/", CurationListView.as_view(), name="curation_list"),
    path("annotation/", AnnotationListView.as_view(), name="annotation_list"),
    path("submission/", SubmissionListView.as_view(), name="submission_list"),

]
