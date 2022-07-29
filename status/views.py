from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
from status.models import *
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig

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
# Get an instance of a logger
logger = logging.getLogger(__name__)



def index(request):
    return HttpResponse("Hello, world. You're at the status index.")

class HomeView(TemplateView):
    template_name = 'index.html'

# Create your views here.
class TargetSpeciesListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = TargetSpecies
    table_class = TargetSpeciesTable
    template_name = 'targetspecies.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}

class OverView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = TargetSpecies
    table_class = OverviewTable
    template_name = 'overview.html'
    export_formats = ['csv', 'tsv','xls','json','yaml']
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

def assembly_team_detail(request, pk=None):
    team = AssemblyTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "assembly_team_detail.html", context)
    return response

def sequencing_team_detail(request, pk=None):
    team = SequencingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "sequencing_team_detail.html", context)
    return response

def curation_team_detail(request, pk=None):
    team = CurationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "curation_team_detail.html", context)
    return response

def collection_team_detail(request, pk=None):
    team = CollectionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "collection_team_detail.html", context)
    return response

def annotation_team_detail(request, pk=None):
    team = AnnotationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "annotation_team_detail.html", context)
    return response

def submission_team_detail(request, pk=None):
    team = SubmissionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "submission_team_detail.html", context)
    return response

class AssemblyProjectListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = AssemblyProject
    table_class = AssemblyProjectTable
    template_name = 'assemblyproject.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class AssemblyListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Assembly
    table_class = AssemblyTable
    template_name = 'assembly.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class SampleCollectionListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = SampleCollection
    table_class = SampleCollectionTable
    template_name = 'collection.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class SpecimenListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Specimen
    table_class = SpecimenTable
    template_name = 'specimens.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class SequencingListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Sequencing
    table_class = SequencingTable
    template_name = 'sequencing.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

    def get_queryset(self):
        """Filter by price if it is provided in GET parameters"""
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
    export_formats = ['csv', 'tsv','xls','json','yaml']

    # def get_queryset(self):
    #     """Filter by price if it is provided in GET parameters"""
    #     queryset = super(SequencingListView, self).get_queryset()
    #     if 'pk' in self.request.GET:
    #         queryset = queryset.filter(pk=self.request.GET['project'])
    #         return queryset

# def SequencingSingleView(request, pk=None):
#     seq = Sequencing.objects.get(pk=pk)
#     context = {"seq": seq
#                }
#     response = render(request, "sequencing_list.html", context)
#     return response

class ReadsListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Reads
    table_class = ReadsTable
    template_name = 'reads.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class CurationListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Curation
    table_class = CurationTable
    template_name = 'curation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class AnnotationListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Annotation
    table_class = AnnotationTable
    template_name = 'annotation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']

class SubmissionListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Submission
    table_class = SubmissionTable
    template_name = 'submission.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xls','json','yaml']
