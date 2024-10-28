"""erga URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView
from django.views.generic.base import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers
from status import api
from django.conf.urls import url
import debug_toolbar
from dal import autocomplete

# API Endpoints
router = routers.DefaultRouter()
router.register(r'kindom', api.TaxonKingdomViewSet)
router.register(r'phylum', api.TaxonPhylumViewSet)
router.register(r'class', api.TaxonClassViewSet)
router.register(r'order', api.TaxonOrderViewSet)
router.register(r'family', api.TaxonFamilyViewSet)
router.register(r'genus', api.TaxonGenusViewSet)
router.register(r'species', api.TargetSpeciesViewSet)
router.register(r'phase', api.PhaseViewSet)
router.register(r'assembly_team', api.AssemblyTeamViewSet)
router.register(r'assembly_project', api.AssemblyProjectViewSet)
router.register(r'assembly_pipeline', api.AssemblyPipelineViewSet)
router.register(r'assembly', api.AssemblyViewSet)
router.register(r'busco_db', api.BUSCOdbViewSet)
router.register(r'busco_version', api.BUSCOversionViewSet)
router.register(r'sample', api.SampleViewSet)
router.register(r'statement', api.StatementViewSet)
router.register(r'specimen', api.SpecimenViewSet)
router.register(r'task', api.TaskViewSet)
router.register(r'country', api.CountryViewSet)
router.register(r'subproject', api.SubprojectViewSet)
router.register(r'sample_collection', api.SampleCollectionViewSet)
router.register(r'sequencing', api.SequencingViewSet)
router.register(r'sequencing_team', api.SequencingTeamViewSet)
router.register(r'hic_team', api.HiCTeamViewSet)
router.register(r'sample_handling_team', api.SampleHandlingTeamViewset)
router.register(r'biobanking_team', api.BiobankingTeamViewSet)
router.register(r'vouchering_team', api.VoucheringTeamViewSet)
router.register(r'barcoding_team', api.BarcodingTeamViewSet)
router.register(r'extraction_team', api.ExtractionTeamViewSet)
router.register(r'taxonomy_team', api.TaxonomyTeamViewSet)
router.register(r'community_annotation_team', api.CommunityAnnotationTeamViewSet)
router.register(r'annotation_team', api.AnnotationTeamViewSet)
router.register(r'genome_team', api.GenomeTeamViewSet)
router.register(r'from_manifest', api.FromManifestViewSet)
router.register(r'reads', api.ReadsViewSet)
router.register(r'enareads', api.EnaReadsViewSet)
router.register(r'run', api.RunViewSet)
router.register(r'ena_run', api.EnaRunViewSet, basename='enarun')
router.register(r'collection_team', api.CollectionTeamViewSet)
# router.register(r'tag', api.TagViewSet)
router.register(r'recipe', api.RecipeViewSet)
router.register(r'affiliation', api.AffiliationViewSet)
router.register(r'user_profile', api.UserProfileViewSet)
router.register(r'person', api.PersonViewSet)


urlpatterns = [
    url(r'^api/', include(router.urls), name="api"),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^', include('status.urls')),
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^accounts/', include('allauth.urls')),
    path('__debug__/', include(debug_toolbar.urls)),
    url(
        r'^django_popup_view_field/',
        include('django_popup_view_field.urls', namespace="django_popup_view_field")
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
