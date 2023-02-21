from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
from status.models import *
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.edit import FormView
from django.views.generic.edit import UpdateView
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig
from django_addanother.views import CreatePopupMixin

from status.tables import *
from django_tables2.export.views import ExportMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
#from status.filters import SpeciesFilter
from django.utils.safestring import mark_safe
from math import log
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import Count
from django.db.models import Q
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import subprocess
import json
import os, time, sys
import scipy.stats as stats
import networkx as nx
from timeit import default_timer as timer
from datetime import timedelta
import pickle
import logging
from django.contrib import messages
from django.views.generic.edit import CreateView
from django_addanother.views import CreatePopupMixin
import requests
from django.shortcuts import get_object_or_404
#from status.filters import SpecimenFilter
#from status.forms import (EditProfileForm, ProfileForm)
from status.forms import ProfileUpdateForm
from django.urls import reverse_lazy



# Get an instance of a logger
logger = logging.getLogger(__name__)



class AffiliationCreateView(CreatePopupMixin, CreateView):
    model = Affiliation
    template_name = 'affiliation_form.html'
    fields = ['affiliation']

def index(request):
    return HttpResponse("Hello, world. You're at the status index.")

class HomeView(TemplateView):
    template_name = 'index.html'

class SuccessView(TemplateView):
    template_name = 'success.html'

# Create your views here.
class TargetSpeciesListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = TargetSpecies
    table_class = TargetSpeciesTable
    template_name = 'targetspecies.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    # def get_queryset(self):
    #     return TargetSpecies.objects.all().order_by('taxon_kingdom').values()

class OverView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = TargetSpecies
    table_class = OverviewTable
    template_name = 'overview.html'
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}


def species_detail(request, pk=None, scientific_name=None):
    if pk:
        sp = TargetSpecies.objects.get(pk=pk)
    else:
        sp = TargetSpecies.objects.get(scientific_name=scientific_name)
        pk = TargetSpecies.pk
    context = {"species": sp
               }
    response = render(request, "species_detail.html", context)
    return response

@permission_required("status.assembly_team_detail", login_url='access_denied')
def assembly_team_detail(request, pk=None):
    team = AssemblyTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.sample_handling_team_detail", login_url='access_denied')
def sample_handling_team_detail(request, pk=None):
    team = SampleHandlingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.taxonomy_team_detail", login_url='access_denied')
def taxonomy_team_detail(request, pk=None):
    team = TaxonomyTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.vouchering_team_detail", login_url='access_denied')
def vouchering_team_detail(request, pk=None):
    team = VoucheringTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.biobanking_team_detail", login_url='access_denied')
def biobanking_team_detail(request, pk=None):
    team = BiobankingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.barcoding_team_detail", login_url='access_denied')
def barcoding_team_detail(request, pk=None):
    team = BarcodingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.sequencing_team_detail", login_url='access_denied')
def sequencing_team_detail(request, pk=None):
    team = SequencingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.extraction_team_detail", login_url='access_denied')
def extraction_team_detail(request, pk=None):
    team = ExtractionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.curation_team_detail", login_url='access_denied')
def curation_team_detail(request, pk=None):
    team = CurationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.collection_team_detail", login_url='access_denied')
def collection_team_detail(request, pk=None):
    team = CollectionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.community_annotation_team_detail", login_url='access_denied')
def community_annotation_team_detail(request, pk=None):
    team = CommunityAnnotationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.annotation_team_detail", login_url='access_denied')
def annotation_team_detail(request, pk=None):
    team = AnnotationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

class AssemblyProjectListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = AssemblyProject
    table_class = AssemblyProjectTable
    template_name = 'assemblyproject.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_queryset(self):
        queryset = super(AssemblyProjectListView, self).get_queryset()
        if 'project' in self.request.GET:
            queryset = queryset.filter(pk=self.request.GET['project'])
            return queryset

class AssemblyListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Assembly
    table_class = AssemblyTable
    template_name = 'assembly.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

def assembly_pipeline_detail(request, pk=None):
    pipeline = AssemblyPipeline.objects.get(pk=pk)
    context = {"pipeline": pipeline
               }
    response = render(request, "assembly_pipeline_detail.html", context)
    return response

class SampleCollectionListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = SampleCollection
    table_class = SampleCollectionTable
    template_name = 'collection.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class SpecimenListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Specimen
    table_class = SpecimenTable
    #filterset_class = SpecimenFilter
    template_name = 'specimens.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_queryset(self):
        #self.id = get_object_or_404(Specimen, pk=self.kwargs['id'])
        if 'id' in self.kwargs:
            return Specimen.objects.filter(pk=self.kwargs['id'])
        if 'collection' in self.kwargs:
            return Specimen.objects.filter(collection=self.kwargs['collection'])
    
class SampleListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Sample
    table_class = SampleTable
    template_name = 'samples.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

def copo_record(request, copoid):
    r=requests.get("https://copo-project.org/api/sample/copo_id/"+ copoid)
    resp = ""
    if(r.status_code == 200):
        resp=r.json()
    else:
        resp = {'number_found':0}
    #output = json.dumps(json.loads(output), indent=4))
    #return HttpResponse(output, content_type="application/json")
    return render(request,'copo.html',{'response':resp})
    

class SequencingListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Sequencing
    table_class = SequencingTable
    template_name = 'sequencing.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    def get_queryset(self):
        queryset = super(SequencingListView, self).get_queryset()
        if 'project' in self.request.GET:
            queryset = queryset.filter(pk=self.request.GET['project'])
            return queryset


class SequencingDetailView(DetailView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Sequencing
    table_class = SequencingTable
    queryset = Sequencing.objects.all()
    template_name = 'sequencing_detail.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}

class ReadsListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Reads
    table_class = ReadsTable
    template_name = 'reads.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class CurationListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Curation
    table_class = CurationTable
    template_name = 'curation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class AnnotationListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Annotation
    table_class = AnnotationTable
    template_name = 'annotation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class CommunityAnnotationListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = CommunityAnnotation
    table_class = CommunityAnnotationTable
    template_name = 'community_annotation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']


class AccessDeniedView(TemplateView):
    template_name = 'denied.html'

class GenomeTeamsView(ExportMixin, SingleTableMixin, FilterView):
    model = GenomeTeam
    table_class = GenomeTeamsTable
    template_name = 'genometeams.html'
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}

@permission_required("status.user_profile", login_url='access_denied')
def user_profile(request, pk=None):
    profile = UserProfile.objects.get(pk=pk)
    context = {"profile": profile
               }
    response = render(request, "user_profile.html", context)
    return response

class AuthorsView(ExportMixin, SingleTableMixin, FilterView):
    model = Author
    table_class = AuthorsTable
    template_name = 'authors.html'
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}

# @login_required
# def edit_profile(request):
#     if request.method == 'POST':
#         form = EditProfileForm(request.POST, instance=request.user)
#         profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.userprofile)  # request.FILES is show the selected image or file

#         if form.is_valid() and profile_form.is_valid():
#             user_form = form.save()
#             custom_form = profile_form.save(False)
#             custom_form.user = user_form
#             custom_form.save()
#             return redirect('status:user_profile')
#     else:
#         form = EditProfileForm(instance=request.user)
#         profile_form = ProfileForm(instance=request.user.userprofile)
#         args = {}
#         # args.update(csrf(request))
#         args['form'] = form
#         args['profile_form'] = profile_form
#         return render(request, 'edit_profile.html', args)
class EditProfileView(FormView):
    model = UserProfile
    fields = ['first_name','middle_name','last_name','affiliation','orcid','roles','lead']
    template_name = 'status/userprofile_update_form.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('success')

    def get_form(self, form_class = ProfileUpdateForm):
        """
        Check if the user already saved contact details. If so, then show
        the form populated with those details, to let user change them.
        """
        try:
            profile = UserProfile.objects.get(user=self.request.user)
            return form_class(instance=profile, **self.get_form_kwargs())
        except UserProfile.DoesNotExist:
            return form_class(**self.get_form_kwargs())

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.save()
        return super(EditProfileView, self).form_valid(form)
    
class LogView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = StatusUpdate
    table_class = StatusUpdateTable
    template_name = 'log.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    # def get_queryset(self):
    #     queryset = super(StatusUpdate, self).get_queryset()
    #     if 'project' in self.request.GET:
    #         queryset = queryset.filter(pk=self.request.GET['species'])
    #         return queryset

class SpeciesLogView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = StatusUpdate
    table_class = StatusUpdateTable
    template_name = 'log.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    def get_queryset(self):
        #species = TargetSpecies.objects.get(scientfic_name=self.request.GET['scientific_name'])
        queryset = super(SpeciesLogView, self).get_queryset()
        # if 'pk' in self.request.GET:
        queryset = queryset.filter(species=self.request.GET['id'])
        return queryset


