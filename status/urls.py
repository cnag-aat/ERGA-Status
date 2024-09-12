from django.urls import path
from django.conf.urls import url
from django.contrib import admin
from . import views
from status.views import TargetSpeciesListView
from status.views import AssemblyListView
from status.views import SampleCollectionListView
from status.views import SequencingListView
from status.views import SequencingDetailView
from status.views import RunListView
from status.views import ReadsListView
from status.views import AssemblyProjectListView
from status.views import CurationListView
from status.views import AnnotationListView
from status.views import CommunityAnnotationListView
# from status.views import SubmissionListView
from status.views import SpecimenListView
from status.views import SampleListView
#from status.views import HomeView
from status.views import OverView
from status.views import AccessDeniedView
from status.views import GenomeTeamsView
from status.views import AffiliationCreateView
from status.views import AuthorsView
from status.views import EditProfileView
from status.views import SuccessView
from status.views import LogView
from status.views import SpeciesLogView
from status.views import GoaTListView
# from status.views import NewSpeciesView
from status.views import NewSpeciesListView
from status.views import HelpView


urlpatterns = [
    path("", views.home, name="home"),
    path("overview/", OverView.as_view(), name="overview"),
    path("log/", LogView.as_view(), name="log"),
    path("log/?species=<int:id>/", SpeciesLogView.as_view(), name="species_log"),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
    path("goat/", GoaTListView.as_view(), name="goat_list"),
    path("goat/?task=<int:task>", GoaTListView.as_view(), name="goat_list"),
    path("species/<int:pk>/", views.species_detail, name="species_detail"),
    path("species/?scientific_name=<scientific_name>", views.species_detail, name="species_detail"),
    path("assemblies/", AssemblyListView.as_view(), name="assembly_list"),
    path("specimens/", SpecimenListView.as_view(), name="specimen_list"),
    path("specimens/?collection=<collection>", SpecimenListView.as_view(), name="specimen_list"),
    path("specimens/<int:id>/", SpecimenListView.as_view(), name="specimen_list"),
    path("from_manifest/?specimen_id=<specimen_id>", views.from_manifest_detail, name="from_manifest_detail"),
    path("from_manifest/<int:pk>/", views.from_manifest_detail, name="from_manifest_detail"),
    path("samples/", SampleListView.as_view(), name="sample_list"),
    path("samples/<int:pk>/", views.sample_detail, name="sample_detail"),
    path("projects/", AssemblyProjectListView.as_view(), name="assembly_project_list"),
    path("projects/?species=<scientific_name>", AssemblyProjectListView.as_view(), name="assembly_project_list"),
    path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("collection_team/<int:pk>/", views.collection_team_detail, name="collection_team_detail"),
    path("sequencing_team/<int:pk>/", views.sequencing_team_detail, name="sequencing_team_detail"),
    path("hic_team/<int:pk>/", views.hic_team_detail, name="hic_team_detail"),
    path("extraction_team/<int:pk>/", views.extraction_team_detail, name="extraction_team_detail"),
    path("assembly_team/<int:pk>/", views.assembly_team_detail, name="assembly_team_detail"),
    path("curation_team/<int:pk>/", views.curation_team_detail, name="curation_team_detail"),
    path("annotation_team/<int:pk>/", views.annotation_team_detail, name="annotation_team_detail"),
    path("sample_handling_team/<int:pk>/", views.sample_handling_team_detail, name="sample_handling_team_detail"),
    path("taxonomy_team/<int:pk>/", views.taxonomy_team_detail, name="taxonomy_team_detail"),
    path("vouchering_team/<int:pk>/", views.vouchering_team_detail, name="vouchering_team_detail"),
    path("biobanking_team/<int:pk>/", views.biobanking_team_detail, name="biobanking_team_detail"),
    path("barcoding_team/<int:pk>/", views.barcoding_team_detail, name="barcoding_team_detail"),
    path("community_annotation_team_detail/<int:pk>/", views.community_annotation_team_detail, name="community_annotation_team_detail"),
    # path("submission_team/<int:pk>/", views.submission_team_detail, name="submission_team_detail"),
    path("pipeline/<int:pk>/", views.assembly_pipeline_detail, name="assembly_pipeline_detail"),
    url('collection/?species=<species_id>', SampleCollectionListView.as_view(), kwargs=None, name="collection_list"),
    # path("sequencing/<project>/", SequencingListView.as_view(), kwargs=None, name="sequencing_list"),
    path("curation/?species=<scientific_name>", CurationListView.as_view(), name="curation_list"),
    path("annotation/?species=<scientific_name>", AnnotationListView.as_view(), name="annotation_list"),
    path("community_annotation/?species=<scientific_name>", CommunityAnnotationListView.as_view(), name="community_annotation_list"),
    # path("submission/?species=<scientific_name>", SubmissionListView.as_view(), name="submission_list"),
    path("collection/", SampleCollectionListView.as_view(), name="collection_list"),
    path("sequencing/", SequencingListView.as_view(), name="sequencing_list"),
    path("sequencing/?species=<scientific_name>", SequencingListView.as_view(), name="sequencing_list"),
    path("reads/", ReadsListView.as_view(), name="reads_list"),
    path("reads/?project=<project>", ReadsListView.as_view(), name="reads_list"),
    path("runs/", RunListView.as_view(), name="runs_list"),
    path("curation/", CurationListView.as_view(), name="curation_list"),
    path("annotation/", AnnotationListView.as_view(), name="annotation_list"),
    path("community_annotation/", CommunityAnnotationListView.as_view(), name="community_annotation_list"),
    # path("submission/", SubmissionListView.as_view(), name="submission_list"),
    path('access_denied/', AccessDeniedView.as_view(), name="access_denied"),
    path('teams/', GenomeTeamsView.as_view(), name="genome_teams"),
    path('create_affiliation/', AffiliationCreateView.as_view(), name="create_affiliation"),
    path("user_profile/<int:pk>/", views.user_profile, name="user_profile"),
    path("person/<int:pk>/", views.person_detail, name="person_detail"),
    path("copo/<str:copoid>/", views.copo_record, name="copo"),
    path('authors/', AuthorsView.as_view(), name="author_list"),
    path('edit_profile/', EditProfileView.as_view(), name="edit_profile"),
    path('add_species_list/', NewSpeciesListView.as_view(), name="add_species_list"),
    # path('add_species/', NewSpeciesView.as_view(), name="add_species"),
    path('success/', SuccessView.as_view(), name="success"),
    path("recipe/<int:pk>/", views.recipe_detail, name="recipe_detail"),
    path("help/", HelpView.as_view(), name="help"),
]

admin.site.site_header = "ERGA-GTC Admin"
admin.site.site_title = "ERGA-GTC Admin Portal"
admin.site.index_title = "Welcome to the ERGA Genome Tracking Console"