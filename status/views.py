from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
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
from django.db.models import Sum
from django_tables2.export.views import ExportMixin
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin
#from status.filters import SpeciesFilter
from django.utils.safestring import mark_safe
from math import log
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models import Q
from django.db.models import F, Value
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from collections import defaultdict

import subprocess
import json
import os, time, sys, re
import scipy.stats as stats
import networkx as nx
from timeit import default_timer as timer
from datetime import timedelta
from datetime import datetime
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
# from status.forms import NewSpeciesForm
from status.forms import NewSpeciesListForm
from django.urls import reverse, reverse_lazy
from status.filters import GenomeTeamFilter
from status.filters import OverviewSpeciesFilter
from status.filters import SpeciesFilter
from status.filters import ReadsFilter
from status.filters import AssemblyFilter
from status.filters import SpecimenFilter
from status.filters import SampleFilter
from status.filters import SampleCollectionFilter
from status.filters import EARReviewFilter
from status.filters import SequencingFilter
from status.filters import AssemblyProjectFilter
from braces.views import GroupRequiredMixin
from django.db.models import OuterRef, Subquery
from django.core.cache import cache
from django.db.models.functions import Coalesce
from django_cron import CronJobBase, Schedule
from datetime import datetime
import logging
import re
from unicodedata import normalize
from unidecode import unidecode
import yaml
import urllib
from urllib import request
from .aggregates import GroupConcat

# Get an instance of a logger
# logger = logging.getLogger(__name__)
# import logging

# Create a logger for your app
logger = logging.getLogger('status')
COPO_URL = "https://copo-project.org/api"
CBP_URL = "https://dades.biogenoma.cat/api/biosamples?taxid__in={taxid}"
ENA_BIOSAMPLES_URL = "https://www.ebi.ac.uk/biosamples/samples"

def month_matching(date_str):
    try:
        return bool(datetime.strptime(date_str, '%Y-%m'))
    except ValueError:
        return False

def date_matching(date_str):
    try:
        return bool(datetime.strptime(date_str, '%Y-%m-%d'))
    except ValueError:
        return False

class AffiliationCreateView(CreatePopupMixin, CreateView):
    model = Affiliation
    template_name = 'affiliation_form.html'
    fields = ['affiliation']

class ResearchGroupCreateView(CreatePopupMixin, CreateView):
    model = ResearchGroup
    template_name = 'research_group_form.html'
    fields = ['name']

def index(request):
    return HttpResponse("Hello, world. You're at the status index.")

class HelpView(TemplateView):
    template_name = 'help.html'

    
def phylogenetic_chart_data(request):
    """
    API endpoint to provide phylogenetic data for D3.js chart
    Returns species organized by phylum and family
    """
    # Query all target species with their taxonomy information
    species_list = TargetSpecies.objects.filter(
        phylum__isnull=False
    ).exclude(
        phylum__name=''
    ).values(
        'scientific_name',
        'phylum__name',
        'family__name'
    )
    
    # Convert to list format for JSON serialization
    data = []
    for species in species_list:
        data.append({
            'name': species['scientific_name'],
            'phylum': species['phylum__name'] or 'Unknown',
            'family': species['family__name'] or 'Unknown'
        })
    
    return JsonResponse({
        'species': data
    })    

def home(request):
    centerlabels = []
    waiting = []
    collected = []
    not_collected = []
    sequencing = []
    seq_done = []
    assembling = []
    assembly_done = []
    assembly_dropped = []
    total_collected = []
    total_not_collected = []
    total_sequencing = []
    total_seq_done = []
    total_assembling = []
    total_assembly_done = []
    total_submitted = []
   # speciesdict = {}
    dropped_set = {'Abandoned'}
    in_production_set = {'Prep', 'Sequencing', 'TopUp', 'Extracted'}
    #in_production_set = {'Received', 'Prep', 'Sequencing', 'TopUp', 'Extracted'}
    seq_done_set = {'Done', 'Submitted'}
    in_assembly_set = {'Issue','Assembling', 'Contigs','Scaffolding','Scaffolds','Curating','Done'}
    assembly_done_set = {'Approved','Submitted','UnderReview'}

    #seq_centers = SequencingTeam.objects.annotate(gspan=Sum("genometeam__species__genome_size"))
    seq_centers = SequencingTeam.objects.all()
    for c in seq_centers:
        centerlabels.append(c.name)
        #assigned.append(c.gspan)
        waiting_span = 0
        not_collected_span = 0
        collected_span = 0
        sequencing_span = 0
        seq_done_span = 0
        assembling_span = 0
        assembly_done_span = 0
        assembly_dropped_span = 0
        submitted_span = 0
        #.filter(sequencing_rel__long_seq_status='Done')
        queryset = TargetSpecies.objects.filter(gt_rel__sequencing_team=c)
        if (queryset):
            for sp in queryset:
                #assigned_span += sp.genome_size
                if (sp.assembly_rel.status in assembly_done_set):
                        assembly_done_span += sp.genome_size_update
                else:
                    if (sp.assembly_rel.status in dropped_set):
                        assembly_dropped_span += sp.genome_size_update
                    else:
                        if ((sp.assembly_rel.status in in_assembly_set) and (sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                            assembling_span += sp.genome_size_update
                        else:
                            if ((sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                                seq_done_span += sp.genome_size_update
                            else: 
                                if ((sp.sequencing_rel.long_seq_status in in_production_set) or (sp.sequencing_rel.hic_seq_status in in_production_set) or (sp.sequencing_rel.long_seq_status in seq_done_set) or (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                                    sequencing_span += sp.genome_size_update
                                else:
                                    if ((sp.goat_sequencing_status == 'sample_collected') or (sp.goat_sequencing_status == 'sample_acquired')):
                                        collected_span += sp.genome_size_update
                                    else:
                                        not_collected_span += sp.genome_size_update

                         
            # goat_sequencing_status
            not_collected.append(not_collected_span/1000000000)
            collected.append(collected_span/1000000000)
            sequencing.append(sequencing_span/1000000000)
            seq_done.append(seq_done_span/1000000000)
            assembling.append(assembling_span/1000000000)
            assembly_done.append(assembly_done_span/1000000000)
            assembly_dropped.append(assembly_dropped_span/1000000000)
        else:
            not_collected.append(0)
            collected.append(0)
            sequencing.append(0)
            seq_done.append(0)
            assembling.append(0)
            assembly_done.append(0)
            assembly_dropped.append(0)

#### TOTALS


    total_not_collected_span = 0
    total_collected_span = 0
    total_sequencing_span = 0
    total_seq_done_span = 0
    total_assembling_span = 0
    total_assembly_done_span = 0
    total_assembly_dropped_span = 0
    total_not_collected_count = 0
    total_collected_count = 0
    total_sequencing_count = 0
    total_seq_done_count = 0
    total_assembling_count = 0
    total_assembly_done_count = 0
        #.filter(sequencing_rel__long_seq_status='Done')
    allqueryset = TargetSpecies.objects.all().exclude(goat_target_list_status = None).exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed')

    if (allqueryset):
        for sp in allqueryset:
            #assigned_span += sp.genome_size
            if not sp.genome_size_update:
                sp.genome_size_update = 0;
            if (sp.assembly_rel and sp.assembly_rel.status in assembly_done_set):
                    total_assembly_done_span += sp.genome_size_update
                    total_assembly_done_count += 1
            else:

                if (sp.assembly_rel and sp.assembly_rel.status in dropped_set):
                        total_assembly_dropped_span += sp.genome_size_update
                else:
                    if ((sp.assembly_rel.status in in_assembly_set) and (sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                        total_assembling_span += sp.genome_size_update
                        total_assembling_count += 1
                    else:
                        if ((sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                            total_seq_done_span += sp.genome_size_update
                            total_seq_done_count += 1
                        else:
                            if ((sp.sequencing_rel.long_seq_status in in_production_set) or (sp.sequencing_rel.hic_seq_status in in_production_set) or (sp.sequencing_rel.long_seq_status in seq_done_set) or (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                                total_sequencing_span += sp.genome_size_update
                                total_sequencing_count += 1
                            else:
                                if ((sp.goat_sequencing_status == 'sample_collected') or (sp.goat_sequencing_status == 'sample_acquired')):
                                    total_collected_span += sp.genome_size_update
                                    total_collected_count += 1
                                else:
                                    total_not_collected_span += sp.genome_size_update
                                    total_not_collected_count += 1


    # goat_sequencing_status
    total_not_collected_span = total_not_collected_span/1000000000
    total_collected_span = total_collected_span/1000000000
    total_sequencing_span = total_sequencing_span/1000000000
    total_seq_done_span = total_seq_done_span/1000000000
    total_assembling_span = total_assembling_span/1000000000
    total_assembly_done_span = total_assembly_done_span/1000000000
    total_assembly_dropped_span = total_assembly_done_span/1000000000
            
    phylo_data = []
    for species in allqueryset:
        if (species.assembly_rel.status in assembly_done_set):
            phylo_data.append({
                'name': species.scientific_name,
                'phylum': (
                    species.taxon_phylum.name
                    if species.taxon_phylum and species.taxon_phylum.name
                    else 'Unknown'
                ),
                'class': (
                    species.taxon_class.name
                    if species.taxon_class and species.taxon_class.name
                    else 'Unknown'
                ),
                'family': (
                    species.taxon_family.name
                    if species.taxon_family and species.taxon_family.name
                    else 'Unknown'
                )
            })
    return render(request, 'index.html', {
        'centers': centerlabels,
        'not_collected': not_collected,  
        'collected': collected,
        'sequencing': sequencing,
        'seq_done': seq_done,
        'assembling': assembling,
        'assembly_done': assembly_done,
        'total_not_collected': total_not_collected_span,
        'total_collected': total_collected_span,
        'total_sequencing': total_sequencing_span,
        'total_seq_done': total_seq_done_span,
        'total_assembling': total_assembling_span,
        'total_assembly_done': total_assembly_done_span,
        'total_assembly_dropped': total_assembly_dropped_span,
        'total_not_collected_count': total_not_collected_count,
        'total_collected_count': total_collected_count,
        'total_sequencing_count': total_sequencing_count,
        'total_seq_done_count': total_seq_done_count,
        'total_assembling_count': total_assembling_count,
        'total_assembly_done_count': total_assembly_done_count,
        'phylo_data': json.dumps(phylo_data)
    })

class SuccessView(TemplateView):
    template_name = 'success.html'

# Create your views here.
def _copo_hidden():
    """True if the active customization disables COPO display."""
    custom = Customization.objects.first()
    return bool(custom and not custom.show_copo)


def _drop_copo_filter(filterset):
    """Remove the copo_status filter (and its form field) from a filterset in place."""
    if filterset is not None and 'copo_status' in filterset.filters:
        filterset.filters.pop('copo_status')
        if 'form' in filterset.__dict__:
            del filterset.__dict__['form']
    return filterset


class TargetSpeciesListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin,
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = TargetSpecies
    table_class = TargetSpeciesTable
    template_name = 'targetspecies.html'
    filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Species'
        return context

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        if _copo_hidden():
            kwargs['exclude'] = list(kwargs.get('exclude', [])) + ['copo_status']
        return kwargs

    def get_filterset(self, filterset_class):
        fs = super().get_filterset(filterset_class)
        if _copo_hidden():
            _drop_copo_filter(fs)
        return fs

    def get_queryset(self):
        return TargetSpecies.objects.exclude(goat_target_list_status = None).exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed')
        #return TargetSpecies.objects.exclude(goat_sequencing_status = None).exclude(goat_sequencing_status = '')

    # def get_queryset(self):
    #     return TargetSpecies.objects.all().order_by('taxon_kingdom').values()

class GoaTListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    model = TargetSpecies
    table_class = GoaTSpeciesTable
    template_name = 'goatlist.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100000}
    export_formats = ['csv', 'tsv','xlsx','json']

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["last_updated"] = TargetSpecies.objects.order_by('-date_updated')[:1].get().date_updated
        context['build_page_title'] = 'GTC GoaT List'
        return context

    def get_queryset(self):
        # Base queryset with combined exclusion conditions
        queryset = TargetSpecies.objects.exclude(
            Q(goat_target_list_status='none') |
            Q(goat_target_list_status='waiting_list') |
            Q(goat_target_list_status='removed')
        )
        
        # Filter by task if provided in GET request
        task = self.request.GET.get('task')
        if task:
            # Query directly for species IDs associated with the provided task
            species_ids = SampleCollection.objects.filter(task=task).values_list("species", flat=True).distinct()
            return queryset.filter(id__in=species_ids)
        
        # If no task, get all species IDs associated with any task
        species_with_task = SampleCollection.objects.filter(task__isnull=False).values_list("species", flat=True).distinct()
        return queryset.filter(id__in=species_with_task)

    # def get_queryset(self):

    #     queryset = TargetSpecies.objects.all().exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = 'waiting_list').exclude(goat_target_list_status = 'removed')
    #     #queryset = queryset.annotate(subproject=Subquery(SampleCollection.objects.filter(subproject=OuterRef('pk')).first()))
        
    #     if self.request.method == 'GET' and 'task' in self.request.GET: #self.request.GET['task'] is not None:
    #         species_ids = SampleCollection.objects.filter(task=self.request.GET['task']).values_list("species", flat=True).distinct()
    #         return queryset.filter(id__in=species_ids)
    #     else:
    #         taskset = Task.objects.all()
    #         species_with_task = []
    #         for t in taskset:
    #             species_ids = SampleCollection.objects.filter(task=t).values_list("species", flat=True).distinct()
    #             species_with_task.extend(species_ids)
    #         return queryset.filter(id__in=species_with_task)

class OverView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    login_url = "access_denied"
    model = TargetSpecies
    table_class = OverviewTable
    template_name = 'overview.html'
    filterset_class = OverviewSpeciesFilter
    export_formats = ['csv', 'tsv','xlsx','json']
    table_pagination = {"per_page": 100}




    def get_context_data(self, *args, **kwargs):
        data = super(OverView, self).get_context_data(*args, **kwargs)
        data['build_page_title'] = 'GTC OverView'
        return data

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        if _copo_hidden():
            kwargs['exclude'] = list(kwargs.get('exclude', [])) + ['copo_status']
        return kwargs

    def get_filterset(self, filterset_class):
        fs = super().get_filterset(filterset_class)
        if _copo_hidden():
            _drop_copo_filter(fs)
        return fs

    def get_queryset(self):
        latest_status = StatusUpdate.objects.filter(
            species=OuterRef("pk")
        ).order_by("-timestamp")
        queryset = super().get_queryset().annotate(
            latest_status_ts=Subquery(
                latest_status.values("timestamp")[:1]
            )
        )
        ordered_queryset = queryset.order_by(
            '-gss_rank', '-assembly_rel__assembly_rank', #'collection_rel__copo_status',
            'taxon_kingdom', 'taxon_phylum', 'taxon_class', 'taxon_order',
            'taxon_family', 'taxon_genus', 'scientific_name'
        )
        filtered_queryset = ordered_queryset.exclude(goat_target_list_status = None).exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed').exclude(goat_sequencing_status = 'none').exclude(genome_size = None)
        return filtered_queryset

@login_required
def species_detail(request, pk=None, scientific_name=None):
    if pk:
        sp = TargetSpecies.objects.get(pk=pk)
    else:
        sp = TargetSpecies.objects.get(scientific_name=scientific_name)
        pk = TargetSpecies.pk
    sub = SubSpecies.objects.filter(species=sp)

    accepted_ear = None
    active_ear = None
    ear_action = None
    try:
        ap = sp.assembly_rel
        ear = ap.ear_review
        if ear.status == 'accepted':
            accepted_ear = ear
        elif ear.status not in ('declined',):
            active_ear = ear
            if request.user.is_authenticated:
                if EARAssignmentInvite.objects.filter(
                    review=ear, user=request.user, status='pending'
                ).exists():
                    ear_action = 'invite_pending'
                elif ear.status in ('submitted', 'in_review') and ear.reviewers.filter(pk=request.user.pk).exists():
                    ear_action = 'awaiting_your_review'
                elif ear.status == 'reviewer_approved' and ear.supervisor_id == request.user.pk:
                    ear_action = 'awaiting_your_decision'
    except Exception:
        pass

    context = {
        "species": sp,
        "subspecies": sub,
        "accepted_ear": accepted_ear,
        "active_ear": active_ear,
        "ear_action": ear_action,
    }
    response = render(request, "species_detail.html", context)
    return response

@permission_required("status.view_assemblyteam", login_url='access_denied')
def assembly_team_detail(request, pk=None):
    team = AssemblyTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_samplehandlingteam", login_url='access_denied')
def sample_handling_team_detail(request, pk=None):
    team = SampleHandlingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_taxonomyteam", login_url='access_denied')
def taxonomy_team_detail(request, pk=None):
    team = TaxonomyTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_voucheringteam", login_url='access_denied')
def vouchering_team_detail(request, pk=None):
    team = VoucheringTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_biobankingteam", login_url='access_denied')
def biobanking_team_detail(request, pk=None):
    team = BiobankingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_barcodingteam", login_url='access_denied')
def barcoding_team_detail(request, pk=None):
    team = BarcodingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_sequencingteam", login_url='access_denied')
def sequencing_team_detail(request, pk=None):
    team = SequencingTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_hicteam", login_url='access_denied')
def hic_team_detail(request, pk=None):
    team = HiCTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_extractionteam", login_url='access_denied')
def extraction_team_detail(request, pk=None):
    team = ExtractionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_curationteam", login_url='access_denied')
def curation_team_detail(request, pk=None):
    team = CurationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_collectionteam", login_url='access_denied')
def collection_team_detail(request, pk=None):
    team = CollectionTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_communityannotationteam", login_url='access_denied')
def community_annotation_team_detail(request, pk=None):
    team = CommunityAnnotationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_annotationteam", login_url='access_denied')
def annotation_team_detail(request, pk=None):
    team = AnnotationTeam.objects.get(pk=pk)
    context = {"team": team
               }
    response = render(request, "team_detail.html", context)
    return response

@permission_required("status.view_person", login_url='access_denied')
def person_detail(request, pk=None):
    person = Person.objects.get(pk=pk)
    context = {"person": person
               }
    response = render(request, "person_detail.html", context)
    return response

class AssemblyProjectListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin,
    login_url = "access_denied"
    model = AssemblyProject
    table_class = AssemblyProjectTable
    filterset_class = AssemblyProjectFilter
    template_name = 'assemblyproject.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Assembly Status'
        context['assembly_status_choices'] = ASSEMBLY_STATUS_CHOICES
        return context

    def get_queryset(self):
        queryset = super(AssemblyProjectListView, self).get_queryset()
        if 'project' in self.request.GET:
            queryset = queryset.filter(pk=self.request.GET['project'])
            return queryset
        else:
            return AssemblyProject.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')


class AssemblyListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    login_url = "access_denied"
    model = Assembly
    table_class = AssemblyTable
    filterset_class = AssemblyFilter
    template_name = 'assembly.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_queryset(self):
        if 'project' in self.request.GET:
            return Assembly.objects.filter(project_id=self.request.GET['project'])
        # global list: only chromosome-level primary assemblies that are in ENA
        return Assembly.objects.filter(chromosome_level=True).exclude(
            type__in=['Hap2', 'Endosymbiont', 'Alternate', 'MT', 'Chloroplast']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'project' in self.request.GET:
            try:
                project = AssemblyProject.objects.get(pk=self.request.GET['project'])
                context['build_page_title'] = f'Assemblies — {project.species}'
            except AssemblyProject.DoesNotExist:
                context['build_page_title'] = 'Assemblies'
        else:
            context['build_page_title'] = 'ERGA-GTC Assemblies'
        return context


@login_required
def assembly_pipeline_detail(request, pk=None):
    pipeline = AssemblyPipeline.objects.get(pk=pk)
    context = {"pipeline": pipeline
               }
    response = render(request, "assembly_pipeline_detail.html", context)
    return response


@login_required
def assembly_detail(request, pk):
    assembly = get_object_or_404(Assembly, pk=pk)
    ear = getattr(assembly.project, 'ear_review', None)
    context = {
        'assembly': assembly,
        'ear': ear,
        'span_gb': f"{assembly.span / 1e9:.3f}" if assembly.span else None,
        'contig_n50_mb': f"{assembly.contig_n50 / 1e6:.3f}" if assembly.contig_n50 else None,
        'scaffold_n50_mb': f"{assembly.scaffold_n50 / 1e6:.3f}" if assembly.scaffold_n50 else None,
    }
    return render(request, 'assembly_detail.html', context)

class SampleCollectionListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = SampleCollection
    table_class = SampleCollectionTable
    filterset_class = SampleCollectionFilter
    template_name = 'collection.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Sample Collection'
        return context

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        if _copo_hidden():
            kwargs['exclude'] = list(kwargs.get('exclude', [])) + ['copo_status']
        return kwargs

    def get_filterset(self, filterset_class):
        fs = super().get_filterset(filterset_class)
        if _copo_hidden():
            _drop_copo_filter(fs)
        return fs
    def get_queryset(self):
        #return SampleCollection.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')
        return SampleCollection.objects.exclude(
            Q(species__goat_target_list_status='none') |
            Q(species__goat_target_list_status='removed')|
            Q(species__goat_target_list_status=None)|
            Q(species__goat_target_list_status='')|
            Q(species__goat_sequencing_status='none')
        )
class SpecimenListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Specimen
    table_class = SpecimenTable
    filterset_class = SpecimenFilter
    template_name = 'specimens.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Specimens'
        return context
    
    def get_queryset(self):
        #specimens = cache.get('all_specimens')
        #if not specimens:
        #    specimens = Specimen.objects.select_related('species').select_related('collection').select_related('biobanking_team').select_related('nagoya_statement').prefetch_related('collector').prefetch_related('preserver').prefetch_related('identifier').prefetch_related('coordinator')
            #cache.set('all_specimens', specimens)
        #self.id = get_object_or_404(Specimen, pk=self.kwargs['id'])
        if 'id' in self.kwargs:
            return Specimen.objects.filter(pk=self.kwargs['id'])
        if 'collection' in self.kwargs:
            return Specimen.objects.filter(collection=self.kwargs['collection'])
        return Specimen.objects.all()
        
@permission_required("status.from_manifest", login_url='access_denied')
def from_manifest_detail(request, specimen_id=None):
    team = FromManifest.objects.get(specimen_id=specimen_id)
    context = {"team": team
               }
    response = render(request, "from_manifest_detail.html", context)
    return response
        
    
class SampleListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Sample
    table_class = SampleTable
    filterset_class = SampleFilter
    template_name = 'samples.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC GoaT Samples'
        return context
    def get_filterset(self, filterset_class):
        fs = super().get_filterset(filterset_class)
        if _copo_hidden():
            _drop_copo_filter(fs)
        return fs
    def get_queryset(self):
        queryset = super(SampleListView, self).get_queryset().filter(suppressed=False)
        return queryset
#@login_required
def copo_record(request, copoid):
    r=requests.get("https://copo-project.org/api/sample/copo_id/"+ copoid)
    resp = ""
    if(r.status_code == 200):
        if re.search(r'COPO offline',r.text):
            resp = {'number_found':1,'data':[{'copo_id':'COPO is offline','text':r.text}]} #r.headers
        else:
            resp=r.json()
    else:
        resp = {'number_found':0}
    #output = json.dumps(json.loads(output), indent=4))
    #return HttpResponse(output, content_type="application/json")
    return render(request,'copo.html',{'response':resp})
    
class SequencingListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin,
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Sequencing
    table_class = SequencingTable
    template_name = 'sequencing.html'
    filterset_class = SequencingFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Sequencing Status'
        context['sequencing_status_choices'] = SEQUENCING_STATUS_CHOICES
        context['sequencing_status_fields'] = [
            ('long_seq_status',  'Long-read Status'),
            ('short_seq_status', 'Short-read Status'),
            ('hic_seq_status',   'HiC Status'),
            ('rna_seq_status',   'RNA Status'),
        ]
        return context

    def get_queryset(self):
        queryset = super(SequencingListView, self).get_queryset()
        if 'project' in self.request.GET:
            queryset = queryset.filter(pk=self.request.GET['project'])
            return queryset
        else:
            return Sequencing.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')


class SequencingDetailView(LoginRequiredMixin, DetailView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Sequencing
    table_class = SequencingTable
    queryset = Sequencing.objects.all()
    template_name = 'sequencing_detail.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Sequencing'
        return context

class RunListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Run
    table_class = RunTable
    template_name = 'runs.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_queryset(self):
        queryset = super(RunListView, self).get_queryset()
        if 'project' in self.request.GET and self.request.GET['project'] is not '':
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Runs'
        return context

class EnaRunListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = EnaRun
    table_class = EnaRunTable
    template_name = 'enaruns.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_queryset(self):
        queryset = super(EnaRunListView, self).get_queryset()
        if 'project' in self.request.GET and self.request.GET['project'] is not '':
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC ENA Runs'
        return context
       
class ReadsListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Reads
    table_class = ReadsTable
    template_name = 'reads.html'
    filterset_class = ReadsFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Read Data'
        return context
    
    def get_queryset(self):
        queryset = super(ReadsListView, self).get_queryset()
        queryset = queryset.annotate(ont_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='ONT')),
                                     ont_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='ONT'))/(F("project__species__genome_size_update")),
                                     hifi_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiFi')),
                                     hifi_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiFi'))/(F("project__species__genome_size_update")),
                                     short_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='Illumina')),
                                     short_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='Illumina'))/(F("project__species__genome_size_update")),
                                     hic_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiC')),
                                     hic_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiC'))/(F("project__species__genome_size_update")),
                                     rnaseq_pe=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='RNA')),
                                     )
        if 'project' in self.request.GET:
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset

class EnaReadsListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = EnaReads
    table_class = EnaReadsTable
    template_name = 'enareads.html'
    filterset_class = ReadsFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Read Data'
        return context
    
    def get_queryset(self):
        #return TargetSpecies.objects.exclude(goat_target_list_status = None).exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed').exclude(goat_sequencing_status = 'none').exclude(genome_size = None).order_by('-gss_rank','-assembly_rel__assembly_rank','collection_rel__copo_status','taxon_kingdom','taxon_phylum','taxon_class','taxon_order','taxon_family','taxon_genus','scientific_name')
  
        queryset = super(EnaReadsListView, self).get_queryset().exclude(project__species__goat_target_list_status = None).exclude(project__species__goat_target_list_status = 'none').exclude(project__species__goat_target_list_status = '').exclude(project__species__goat_target_list_status = 'removed')
        queryset = queryset.annotate(ena_ont_yield=Coalesce(Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='ONT')),0),
                                     ena_ont_cov=Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='ONT'))/(F("project__species__genome_size_update")),
                                     ena_hifi_yield=Coalesce(Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='HiFi')),0),
                                     ena_hifi_cov=Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='HiFi'))/(F("project__species__genome_size_update")),
                                     ena_short_yield=Coalesce(Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='Illumina')),0),
                                     ena_short_cov=Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='Illumina'))/(F("project__species__genome_size_update")),
                                     ena_hic_yield=Coalesce(Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='HiC')),0),
                                     ena_hic_cov=Sum("ena_run_set__seq_yield",filter=Q(ena_run_set__read_type__startswith='HiC'))/(F("project__species__genome_size_update")),
                                     ena_rnaseq_pe=Coalesce(Sum("ena_run_set__num_reads",filter=Q(ena_run_set__read_type__startswith='RNA')),0),
                                     #data_project=F('ont_ena') if F('ont_ena') else (F('hifi_ena') if F('hifi_ena') else (F('hic_ena') if F('hic_ena') else "")),
                                     )
        if 'project' in self.request.GET:
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset
        
class CurationListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Curation
    table_class = CurationTable
    template_name = 'curation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class AnnotationListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = Annotation
    table_class = AnnotationTable
    template_name = 'annotation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Annotations'
        return context
    def get_queryset(self):
        return Annotation.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')
   
class CommunityAnnotationListView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = CommunityAnnotation
    table_class = CommunityAnnotationTable
    template_name = 'community_annotation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Community Annotations'
        return context
    def get_queryset(self):
        return CommunityAnnotation.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')


class AccessDeniedView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Access Denied'
        return context
    template_name = 'denied.html'

class GenomeTeamsView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    model = GenomeTeam
    login_url = "access_denied"
    table_class = GenomeTeamsTable
    template_name = 'genometeams.html'
    filterset_class = GenomeTeamFilter
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Genome Teams'
        return context
    def get_queryset(self):
        return GenomeTeam.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed') #.exclude(species__goat_sequencing_status = 'none')

@permission_required("status.user_profile", login_url='access_denied')
def user_profile(request, pk=None):
    profile = UserProfile.objects.get(pk=pk)
    context = {"profile": profile,
               'build_page_title':'User Profile'
               }
    response = render(request, "user_profile.html", context)
    return response

class AuthorsView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    login_url = 'access_denied'
    model = Author
    table_class = AuthorsTable
    template_name = 'authors.html'
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Authors'
        return context

class EditProfileView(FormView):
    login_url = "access_denied"
    model = UserProfile
    fields = ['first_name','middle_name','last_name','affiliation','orcid','roles','lead']
    template_name = 'status/userprofile_update_form.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('success')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Edit Profile'
        return context

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
    
class LogView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = StatusUpdate
    table_class = StatusUpdateTable
    template_name = 'log.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Log'
        return context

    # def get_queryset(self):
    #     queryset = super(StatusUpdate, self).get_queryset()
    #     if 'project' in self.request.GET:
    #         queryset = queryset.filter(pk=self.request.GET['species'])
    #         return queryset

class SpeciesLogView(LoginRequiredMixin, ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = StatusUpdate
    table_class = StatusUpdateTable
    template_name = 'log.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Species Log'
        return context

    def get_queryset(self):
        #species = TargetSpecies.objects.get(scientfic_name=self.request.GET['scientific_name'])
        queryset = super(SpeciesLogView, self).get_queryset()
        # if 'pk' in self.request.GET:
        queryset = queryset.filter(species=self.request.GET['id'])
        return queryset

class NewSpeciesListView(GroupRequiredMixin, LoginRequiredMixin, FormView):#GroupRequiredMixin, 
    group_required = "manager"
    login_url = "access_denied"
    # login_url = "access_denied"
    model = SpeciesUpload
    fields = ['file']
    template_name = 'status/new_species_list_form.html'
    form_class = NewSpeciesListForm
    success_url = reverse_lazy("add_species_list") #reverse_lazy('success')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'GTC Upload Species List'
        return context

    def form_valid(self, form):
        gtls_options = ['waiting_list', 'none', 'long_list', 'other_priority', 'family_representative','removed']
        gss_options = ['none', 'in_collection', 'sample_collected', 'sample_acquired', 'data_generation', 'in_assembly','insdc_submitted', 'insdc_open', 'published', 'publication_available' ]
        messages.info(self.request, "Adding...") 
        # form.instance.tag = "bge"
        form.save()
        with open(settings.MEDIA_ROOT + '/' + form.instance.file.name, encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile, delimiter=',')
            # dialect = csv.Sniffer().sniff(csvfile.read(1024))
            # csvfile.seek(0)
            # csvreader = csv.DictReader(csvfile, dialect)
            for row in csvreader:  
                if 'taxon_id' in row:
                    taxid=row['taxon_id']
                    taxid.strip()
                    if re.search(r'\d+', taxid):
                    #if taxid:
                        messages.info(self.request, "Adding taxon: " + taxid) 
                        # try:
                        #     targetspecies = TargetSpecies.objects.get(taxon_id=taxid)
                        # except TargetSpecies.DoesNotExist:
                        #     targetspecies, _ = TargetSpecies.objects.get_or_create(
                        #         taxon_id=taxid
                        #     )
                        targetspecies, created = TargetSpecies.objects.get_or_create(
                            taxon_id=taxid
                        )
                        if (created):     
                            messages.info(self.request, 'added')
                        else:
                            messages.info(self.request,  "updating " + str(targetspecies.listed_species))
                        
                        changed = 0
                        if 'species_name' in row and targetspecies.listed_species is not row['species_name']:
                            targetspecies.listed_species = row['species_name'] or None
                            messages.info(self.request, str(row['species_name']))
                            changed = 1
                        if 'tolid_prefix' in row and targetspecies.tolid_prefix is not row['tolid_prefix']:
                            targetspecies.tolid_prefix = row['tolid_prefix'] or None
                            changed = 1
                        if 'chromosome_number' in row and targetspecies.chromosome_number is not row['chromosome_number']:
                            targetspecies.chromosome_number = row['chromosome_number'] or None
                            changed = 1
                        if 'haploid_number' in row and targetspecies.haploid_number is not row['haploid_number']:
                            targetspecies.haploid_number = row['haploid_number'] or None
                            changed = 1
                        if 'ploidy' in row and targetspecies.ploidy is not row['ploidy']:
                            targetspecies.ploidy = row['ploidy'] or None
                        if 'c_value' in row and targetspecies.c_value is not row['c_value']:
                            targetspecies.c_value = row['c_value'] or None
                            changed = 1
                        if 'genome_size' in row and targetspecies.genome_size is not round(float(row['genome_size'])):
                            targetspecies.genome_size = round(float(row['genome_size'])) or None
                            changed = 1
                        if 'genome_size_update' in row and targetspecies.genome_size_update is not round(float(row['genome_size_update'])):
                            targetspecies.genome_size_update = round(float(row['genome_size_update'])) or None
                            changed = 1
                        # if 'synonym' in row and targetspecies.synonym is not row['synonym']:
                        #     targetspecies.synonym = row['synonym'] or None
                        #     changed = 1
                        if 'goat_target_list_status' in row and targetspecies.goat_target_list_status is not row['goat_target_list_status']:
                            #messages.info(self.request, 'gtls: ' + row['goat_target_list_status'])
                            gtls = row['goat_sequencing_status']
                            if gtls and gtls.strip().lower():
                                if (row['goat_target_list_status'] not in gtls_options):
                                    messages.info(self.request, "Value " + row['goat_target_list_status'] + " not allowed for goat_target_list_status: please fix and try again.")
                                else:
                                    targetspecies.goat_target_list_status = row['goat_target_list_status'] or None
                                    changed = 1
                        else:
                            messages.info(self.request, "No goat_target_list_status field found: please fix and try again.")
                        if 'goat_sequencing_status' in row and targetspecies.goat_sequencing_status is not row['goat_sequencing_status']:
                            #messages.info(self.request, 'gss: ' + row['goat_sequencing_status'])
                            gss = row['goat_sequencing_status']
                            if gss and gss.strip().lower():
                                if (gss not in gss_options):
                                    messages.info(self.request, "Value " + gss + " not allowed for goat_sequencing_status: please fix and try again.")
                                    break
                                if ( gss == "remove" or (targetspecies.goat_sequencing_status == 'none' or targetspecies.goat_sequencing_status == 'in_collection' or targetspecies.goat_sequencing_status == 'sample_collected')):
                                    #messages.info(self.request, gss)
                                    targetspecies.goat_sequencing_status = gss or None
                                    changed = 1
                        if changed:
                            #messages.info(self.request, "saving...")
                            targetspecies.save()
                            changed = 0
                            #messages.info(self.request, "saved")
                        
                        if 'synonym' in row:
                            for syn in row['synonym'].split(','):
                                species_synonyms, created = Synonyms.objects.get_or_create(
                                    name=syn,
                                    species=targetspecies
                                )
                        if 'common_name' in row:
                            for cname in row['common_name'].split(','):
                                species_cnames, created = CommonNames.objects.get_or_create(
                                    name=cname,
                                    species=targetspecies
                                )

                        if ('subspecies_name' in row) and ('subspecies_taxon_id' in row):
                                subspecies_obj, created = SubSpecies.objects.get_or_create(
                                    scientific_name=row['subspecies_name'],
                                    taxon_id=row['subspecies_taxon_id'],
                                    species=targetspecies
                                )
                                
                        if 'ranking' in row and targetspecies.ranking is not row['ranking']:
                            targetspecies.ranking = row['ranking'] or None
                            changed = 1

                        # if 'tags' in row:
                        #     for t in row['tags'].split(' '):
                        #         species_tag, created = Tag.objects.get_or_create(
                        #             tag=t
                        #         )
                        #         targetspecies.tags.add(species_tag)
                        #         changed = 1
                        if changed:
                            #messages.info(self.request, "saving...")
                            targetspecies.save()
                            changed = 0
                            #messages.info(self.request, "saved")
                        
                        # genometeam_record, created = GenomeTeam.objects.get_or_create(
                        #             species=targetspecies
                        #         )
                        if 'task' in row:
                            task, created = Task.objects.get_or_create(
                                    name=row['task']
                                )

                        if 'country' in row:
                            country, created = Country.objects.get_or_create(
                                    name=row['country']
                                )

                        if 'sample_provider_name' in row:
                            spname = row['sample_provider_name']
                            spname.strip()


                        collection_record, created = SampleCollection.objects.get_or_create(
                                    species=targetspecies,
                                    task=task,
                                    country=country,
                                    sample_provider_name=spname
                                )
                        
                        # sequencing_record, created = Sequencing.objects.get_or_create(
                        #             species=targetspecies
                        #         )
                        # assemblyproject_record, created = AssemblyProject.objects.get_or_create(
                        #             species=targetspecies
                        #         )
                        # annotation_record, created = Annotation.objects.get_or_create(
                        #             species=targetspecies
                        #         )
                        # cannotation_record, created = CommunityAnnotation.objects.get_or_create(
                        #             species=targetspecies
                        #         )
                        #Task (= contributing_project_lab on GOAT)	Country	Sample_Provider_Name	Sample_Provider_Email
                        
                        
                        if 'task' in row:
                            task, created = Task.objects.get_or_create(
                                    name=row['task']
                                )
                            collection_record.task = task or None
                            collection_record.subproject.set([task.subproject]) or None

                        if 'country' in row:
                            country, created = Country.objects.get_or_create(
                                    name=row['country']
                                )
                            collection_record.country = country or None

                        if 'sample_provider_name' in row:
                            spname = row['sample_provider_name']
                            if spname and spname.strip():
                                collection_record.sample_provider_name = spname or None

                        if 'sample_provider_email' in row:
                            spemail= row['sample_provider_email']
                            if spemail and spemail.strip():
                                obj = re.search(r'[\w.]+\@[\w.]+', spemail)
                                if obj:
                                    collection_record.sample_provider_email = spemail or None
                                else:
                                    messages.info(self.request, "Value " + spemail + " not a valid email address: please fix and try again.")
                                    break                   
                        
                        # mta1 =  models.BooleanField(default=False, verbose_name="MTA 1: Seq Centers")
                        # mta2 =  models.BooleanField(default=False, verbose_name="MTA 2: LIB leftovers")
                        # barcoding_status = models.CharField(max_length=30, help_text='Barcoding Status', choices=BARCODING_STATUS_CHOICES, default=BARCODING_STATUS_CHOICES[0][0])
                        # barcoding_results = models.CharField(max_length=200, null=True, blank=True)
                        # collection_forecast = models.DateField(blank=True,null=True)
                        # deadline_sampling = models.DateField(blank=True,null=True)
                        # deadline_manifest_sharing = models.DateField(blank=True,null=True)
                        # deadline_manifest_acceptance = models.DateField(blank=True,null=True)
                        # deadline_sample_shipment = models.DateField(blank=True,null=True)
                        # sampling_delay = models.BooleanField(default=False, verbose_name="Delayed sample")
                        if 'mta1' in row:
                            mta1 = row['mta1']
                            if mta1 and mta1.strip():
                                if re.search(r'True',mta1,re.IGNORECASE):
                                #if mta1 == 'True':
                                    collection_record.mta1 = True
                                elif re.search(r'False',mta1,re.IGNORECASE):
                                    collection_record.mta1 = False
                        
                        if 'mta2' in row:
                            mta2 = row['mta2']
                            if mta2 and mta2.strip():
                                if re.search(r'True',mta2,re.IGNORECASE):
                                    collection_record.mta2 = True
                                if re.search(r'False',mta2,re.IGNORECASE):
                                    collection_record.mta2 = False                   

                        if 'sampling_delay' in row:
                            delay = row['sampling_delay']
                            if delay and delay.strip():
                                if re.search(r'True',delay,re.IGNORECASE):
                                    collection_record.sampling_delay = True
                                if re.search(r'False',delay,re.IGNORECASE):
                                    collection_record.sampling_delay = False 
                        
                        if 'sampling_month' in row and collection_record.sampling_month is not row['sampling_month']:
                            smonth = row['sampling_month']
                            

                            if month_matching(smonth):
                                collection_record.sampling_month = smonth or None
                            else:
                                messages.success(self.request, 'sampling_month ' + smonth + ' not in YYYY-MM format') 

                        if 'deadline_manifest_sharing' in row and collection_record.deadline_manifest_sharing is not row['deadline_manifest_sharing']:
                            collection_record.deadline_manifest_sharing = row['deadline_manifest_sharing'] or None

                        if 'deadline_manifest_acceptance' in row and collection_record.deadline_manifest_acceptance is not row['deadline_manifest_acceptance']:
                            collection_record.deadline_manifest_acceptance = row['deadline_manifest_acceptance'] or None

                        if 'deadline_sample_shipment' in row and collection_record.deadline_sample_shipment is not row['deadline_sample_shipment']:
                            collection_record.deadline_sample_shipment = row['deadline_sample_shipment'] or None

                        collection_record.save()
                         
            messages.success(self.request, 'Finished processing uploaded list.')               
            
         
        #return HttpResponseRedirect(self.request.path_info)
        return super(NewSpeciesListView, self).form_valid(form)
 
@login_required
def recipe_detail(request, pk=None):
    recipe = Recipe.objects.get(pk=pk)
    context = {"recipe": recipe,
               'build_page_title':'GTC Recipe'
               }
    response = render(request, "recipe_detail.html", context)
    return response

@login_required
def sample_detail(request, pk=None):
    sample = Sample.objects.get(pk=pk)
    site_url = settings.DEFAULT_DOMAIN
    context = {"sample": sample,
               "site_url": site_url,
               'build_page_title':'GTC Sample'
               }
    response = render(request, "sample_detail.html", context)
    return response



class SpeciesSaveCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440 # every 24 hours

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'status.save_species_cron_job'    # a unique code

    def do(self):
        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        logger.debug(date_time + ": Executing SpeciesSaveCronJob.")
        species = TargetSpecies.objects.all()
        for sp in species:

            logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "SpeciesSaveCronJob: Saving "+ sp.scientific_name)
            sp.save()
            
# import re
# import logging
# import requests
# from datetime import datetime, timedelta
# from unidecode import unidecode
# from django_cron import CronJobBase, Schedule
# from myapp.models import (
#     TargetSpecies, Specimen, Sample, FromManifest,
#     Person, Affiliation, SequencingTeam, GenomeTeam
# )

# logger = logging.getLogger(__name__)


class FetchEARsCronJob(CronJobBase):
    RUN_EVERY_MINS = 480 # every 8 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'status.fetch_ears_cron_job'    # a unique code

    logging.getLogger("requests").setLevel(logging.WARNING)
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.CRITICAL)


    def do(self):
        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        logger.debug(date_time + ": Executing FetchEARsCronJob.")
        owner = "ERGA-consortium"
        repo = "EARs"
        branch = "main"

        def parse_tree(tree):
            files = []
            directories = []
            
            for item in tree:
                if item['type'] == 'blob':  # It's a file
                    files.append(item['path'])
                elif item['type'] == 'tree':  # It's a directory
                    directories.append(item['path'])
            
            return files, directories

        def fetch_repo_tree(owner, repo, branch='main'):
            url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
            headers = {'Accept': 'application/vnd.github+json', 'Authorization':'Bearer '+ settings.GITHUB_TOKEN}
            logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": Fetching using "+ settings.GITHUB_TOKEN)
            try:
                logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": " + url )
                response = requests.get(url, headers=headers)
            except:
                logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": Exception ")
                
                

            logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": " + str(response.status_code))
            
            if response.status_code == 200:
                logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": Fetched data: "+ str(response.status_code)+".")
                return response.json()
            else:
                logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": Failed to fetch data: "+str(response.status_code)+".")
                        
                #print(f"Failed to fetch data: {response.status_code}")
                return None
            
        
        logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: here")
        data = fetch_repo_tree(owner, repo, branch)
        logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: hereafter")
        yaml_files = []
        if data and "tree" in data:
            files, directories = parse_tree(data['tree'])
            # print("Files:")
            # print("\n".join(files))
            # print("\nDirectories:")
            # print("\n".join(directories))
            # example: Assembly_Reports/Valencia_hispanica/fValHis1/fValHis1_EAR.yaml
            for f in files:
                if re.search("^Assembly_Reports.*yaml$", f):
                    yaml_files.append(f)
        else:

            now = datetime.now() # current date and time
            date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
            logger.debug(date_time + ": No tree data found.")

        # json_data = json.loads(r.text)
        # print(json_data)
        #print(yaml_files)
        regular_url_prefix = 'https://github.com/ERGA-consortium/EARs/blob/main/'
        raw_url_prefix = 'https://raw.githubusercontent.com/ERGA-consortium/EARs/refs/heads/main/'
        for yf in yaml_files:
            #print(yf)
            pdf = re.sub(r'yaml$','pdf',yf)
            x = request.urlopen(raw_url_prefix + yf)
            ear_yaml = yaml.safe_load(x)
            logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: "+ yf)

            EAR_pdf = regular_url_prefix + pdf
            #print(ear_yaml['Species'])
            assembly_project= AssemblyProject.objects.all().filter(species__scientific_name=ear_yaml['Species']).first()
            if assembly_project:
                #print(assembly_project)
                logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: " + ear_yaml['Species'])
                for m in ear_yaml['Metrics']:
                    logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: " + m)
                    if re.match(r'^Pre-curation',m):
                        continue
                    if m == 'Curated hap1':
                        ass_type = 'Hap1'
                    elif m == 'Curated pri':
                        ass_type = 'Primary'
                    elif m == 'Curated collapsed':
                        ass_type = 'Primary'

                    assembly = Assembly.objects.all().filter(project=assembly_project).filter(chromosome_level=True).exclude(type='Hap2').exclude(type='Endosymbiont').exclude(type='Alternate').exclude(type='MT').exclude(type='Chloroplast').first()
                    if not assembly:
                        Assembly.objects.create(project=assembly_project,type=ass_type)
                    for assembly_object in Assembly.objects.all().filter(project=assembly_project).filter(chromosome_level=True).exclude(type='Hap2').exclude(type='Endosymbiont').exclude(type='Alternate').exclude(type='MT').exclude(type='Chloroplast'):
                        #assembly_object.type = ass_type #this was redundant
                        
                        if ear_yaml['Metrics'][m].get('Total bp'):
                            assembly_object.span = re.sub(r',','',ear_yaml['Metrics'][m]['Total bp'])
                            #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + assembly_object.span)
                        if ear_yaml['Metrics'][m].get('Scaffold N50'):
                            assembly_object.scaffold_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Scaffold N50'])
                        if ear_yaml['Metrics'][m].get('Contig N50'):
                            assembly_object.contig_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Contig N50'])
                        if ear_yaml['Metrics'][m].get('QV'):
                            assembly_object.qv = ear_yaml['Metrics'][m]['QV']
                            #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + assembly_object.qv)
                            #assembly_object.save()
                        #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + ear_yaml['BUSCO'].get('ver'))
                        if ear_yaml['BUSCO'].get('ver'):
                            if re.search(r'^\d',ear_yaml['BUSCO']['ver']):
                                busco_version = ear_yaml['BUSCO']['ver']
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + busco_version)
                                busco_version_no_space = str(busco_version.split()[0] if busco_version.split() else '')
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + busco_version_no_space)
                                bv, created = BUSCOversion.objects.get_or_create(version=busco_version_no_space)
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + 'after busco version lookup')
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + str(created))
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + str(bv))
                                assembly_object.busco_version = bv
                                assembly_object.save()
                                #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + str(assembly_object.busco_version))
                        if ear_yaml['BUSCO'].get('lineage') is not None and re.search(r'odb',ear_yaml['BUSCO']['lineage']):
                            busco_db = ear_yaml['BUSCO']['lineage']
                            bdb, created = BUSCOdb.objects.get_or_create(db=busco_db)
                            assembly_object.busco_db = bdb
                            assembly_object.save()
                        if (ear_yaml['Metrics'][m].get('BUSCO sing.')):
                            #print('making busco string')
                            busco_s = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO sing.'])
                            busco_d = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO dupl.'])
                            busco_f = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO frag.'])
                            busco_m = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO miss.'])
                            assembly_object.busco  = 'C:{complete:.1f}%[S:{single:.1f}%,D:{duplicate:.1f}%],F:{fragmented:.1f}%,M:{missing:.1f}%'.format(complete = float(busco_s)+float(busco_d), single = float(busco_s), duplicate = float(busco_d), fragmented = float(busco_f), missing = float(busco_m))
                            assembly_object.save()
                            #logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + " FetchEARsCronJob: " + str(assembly_object.busco))
                        assembly_object.report = EAR_pdf
                        assembly_object.save()


# ── EAR Review views ─────────────────────────────────────────────────────────

class EARReviewDetailView(LoginRequiredMixin, DetailView):
    model = EARReview
    template_name = 'ear_review_detail.html'
    context_object_name = 'review'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        review = self.object
        user = self.request.user
        context['build_page_title'] = f'EAR review: {review.assembly_project.species}'

        # Permission flags for the template
        is_submitter = (user == review.submitted_by)
        is_supervisor = (user == review.supervisor)
        is_reviewer = review.reviewers.filter(pk=user.pk).exists()
        context['can_post'] = is_submitter or is_supervisor or is_reviewer
        context['is_submitter'] = is_submitter
        context['is_supervisor'] = is_supervisor
        context['is_reviewer'] = is_reviewer

        # Comments — flat list, ordered by creation
        context['comments'] = (
            review.comments
            .select_related('author', 'parent')
            .prefetch_related('attachments')
            .all()
        )

        # PDF replace permission and version history
        context['can_replace_pdf'] = _can_replace_pdf(user, review)
        context['pdf_versions'] = review.pdf_versions.select_related('uploaded_by').all()

        # Supervisor reviewer management: eligible candidates
        if is_supervisor:
            from django.contrib.auth.models import User, Group
            current_reviewer_ids = list(review.reviewers.values_list('pk', flat=True))
            ear_reviewer_group = Group.objects.filter(name='ear_reviewer').first()
            if ear_reviewer_group:
                candidates = (
                    ear_reviewer_group.user_set
                    .exclude(pk__in=current_reviewer_ids)
                    .exclude(pk=review.submitted_by_id)
                    .order_by('last_name', 'first_name', 'username')
                )
            else:
                candidates = User.objects.none()
            context['reviewer_candidates'] = candidates

        return context


def _can_post_on_review(user, review):
    """A user can post on a review if they are the submitter, supervisor, or a reviewer."""
    if not user.is_authenticated:
        return False
    if user == review.submitted_by or user == review.supervisor:
        return True
    return review.reviewers.filter(pk=user.pk).exists()


def _is_reviewer(user, review):
    return user.is_authenticated and review.reviewers.filter(pk=user.pk).exists()


def _is_supervisor(user, review):
    return user.is_authenticated and user == review.supervisor


# action -> (allowed_roles, allowed_from_statuses, target_status, comment_required, marker)
EAR_ACTIONS = {
    'approve': (['reviewer'],   ['submitted', 'in_review'],                              'reviewer_approved', False, '✓ **Approved**'),
    'reject':  (['reviewer'],   ['submitted', 'in_review', 'reviewer_approved'],         'rejected',          True,  '✗ **Rejected**'),
    'accept':  (['supervisor'], ['reviewer_approved', 'in_review'],                      'accepted',          False, '✓ **Accepted (final)**'),
    'decline': (['supervisor'], ['reviewer_approved'],                                   'declined',          True,  '✗ **Declined**'),
}


@login_required
def ear_review_comment(request, pk):
    """POST handler: add a comment, optionally with a status-changing action (approve/reject/accept/decline)."""
    from status import ear_review as ear_logic

    review = get_object_or_404(EARReview, pk=pk)

    if not _can_post_on_review(request.user, review):
        messages.error(request, "You don't have permission to post on this review.")
        return redirect('ear_review_detail', pk=pk)

    if request.method != 'POST':
        return redirect('ear_review_detail', pk=pk)

    action = request.POST.get('action', 'comment')

    # Validate action permissions and state transition
    if action != 'comment':
        if action not in EAR_ACTIONS:
            messages.error(request, f"Unknown action: {action}")
            return redirect('ear_review_detail', pk=pk)

        roles, from_statuses, _target, comment_required, _marker = EAR_ACTIONS[action]

        is_allowed = (
            ('reviewer' in roles and _is_reviewer(request.user, review)) or
            ('supervisor' in roles and _is_supervisor(request.user, review))
        )
        if not is_allowed:
            messages.error(request, f"You don't have permission to {action} this review.")
            return redirect('ear_review_detail', pk=pk)

        if review.status not in from_statuses:
            messages.error(
                request,
                f"Cannot {action} from status '{review.get_status_display()}'."
            )
            return redirect('ear_review_detail', pk=pk)

        if comment_required and not request.POST.get('body', '').strip():
            messages.error(request, f"A comment is required when you {action}.")
            return redirect('ear_review_detail', pk=pk)

    # Build comment body — prefix with action marker if applicable
    user_body = request.POST.get('body', '').strip()
    if action != 'comment':
        marker = EAR_ACTIONS[action][4]
        body = f"{marker}\n\n{user_body}" if user_body else marker
    else:
        body = user_body

    if not body:
        messages.error(request, "Comment body is empty.")
        return redirect('ear_review_detail', pk=pk)

    # Validate parent FK
    parent_id = request.POST.get('parent') or None
    parent = None
    if parent_id:
        try:
            candidate = EARComment.objects.get(pk=parent_id)
            if candidate.review_id == review.pk:
                parent = candidate
        except EARComment.DoesNotExist:
            pass

    comment = EARComment.objects.create(
        review=review,
        author=request.user,
        body=body,
        parent=parent,
    )

    for f in request.FILES.getlist('attachments'):
        EARAttachment.objects.create(comment=comment, file=f)

    # Apply status change if this was an action
    if action != 'comment':
        review.status = EAR_ACTIONS[action][2]
        review.save(update_fields=['status', 'updated_at'])
        # the post_save signal handles status_change notification + AssemblyProject sync

    ear_logic.notify_new_comment(comment)

    PAST_TENSE = {'approve': 'approved', 'reject': 'rejected', 'accept': 'accepted', 'decline': 'declined'}
    if action == 'comment':
        messages.success(request, "Comment posted.")
    else:
        messages.success(request, f"Review {PAST_TENSE.get(action, action + 'd')}.")

    return redirect('ear_review_detail', pk=pk)


@login_required
def ear_review_create(request):
    """User-facing form to submit a new EAR review."""
    from status.forms import EARReviewCreateForm
    from status import ear_review as ear_logic

    if request.method == 'POST':
        form = EARReviewCreateForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            review = form.save(commit=False)
            review.submitted_by = request.user
            review.save()  # triggers post_save: supervisor auto-assigned, AssemblyProject status synced

            # Reviewer auto-assignment (admin does this in save_related; we mirror it here)
            ear_logic.auto_assign_reviewer(review, added_by=request.user)

            # Optional initial notes become the first comment
            initial = form.cleaned_data.get('initial_comment', '').strip()
            if initial:
                EARComment.objects.create(
                    review=review,
                    author=request.user,
                    body=initial,
                )

            ear_logic.notify_review_submitted(review)

            messages.success(
                request,
                f"EAR review submitted for {review.assembly_project.species}."
            )
            return redirect('ear_review_detail', pk=review.pk)
    else:
        form = EARReviewCreateForm(user=request.user)

    return render(request, 'ear_review_form.html', {
        'form': form,
        'build_page_title': 'Submit EAR for review',
    })


class EARReviewListView(LoginRequiredMixin, SingleTableMixin, FilterView):
    login_url = 'access_denied'
    model = EARReview
    table_class = EARReviewTable
    filterset_class = EARReviewFilter
    template_name = 'ear_review_list.html'
    table_pagination = {'per_page': 50}

    def get_queryset(self):
        return (
            EARReview.objects
            .select_related('assembly_project__species', 'submitted_by')
            .prefetch_related('reviewers')
            .order_by('-updated_at')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'EAR Reviews'
        return context


@login_required
def ear_review_manage_reviewers(request, pk):
    from django.contrib.auth.models import User, Group
    from status import ear_review as ear_logic

    review = get_object_or_404(EARReview, pk=pk)

    if request.user != review.supervisor:
        messages.error(request, "Only the supervisor can manage reviewers.")
        return redirect('ear_review_detail', pk=pk)

    action = request.POST.get('action')

    if action == 'add':
        user_id = request.POST.get('reviewer_id')
        try:
            user = User.objects.get(pk=user_id)
            if not review.reviewers.filter(pk=user.pk).exists():
                EARReviewer.objects.create(
                    review=review,
                    reviewer=user,
                    added_by=request.user,
                )
                if review.status == 'submitted':
                    review.status = 'in_review'
                    review.save(update_fields=['status', 'updated_at'])
                messages.success(request, f"{ear_logic._display_name(user)} added as reviewer.")
            else:
                messages.warning(request, f"{ear_logic._display_name(user)} is already a reviewer.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    elif action == 'remove':
        user_id = request.POST.get('reviewer_id')
        try:
            user = User.objects.get(pk=user_id)
            EARReviewer.objects.filter(review=review, reviewer=user).delete()
            messages.success(request, f"{ear_logic._display_name(user)} removed from reviewers.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('ear_review_detail', pk=pk)


def ear_assignment_response(request, token, response):
    """Handle Yes/No assignment confirmation links sent by email."""
    from django.core import signing
    from status import ear_review as ear_logic

    try:
        data = ear_logic.load_assignment_token(token)
    except signing.BadSignature:
        messages.error(request, "This assignment link is invalid or has expired.")
        return redirect('ear_review_list')

    review = get_object_or_404(EARReview, pk=data['review'])
    user_id = data['user']
    role = data['role']

    if response == 'yes':
        ear_logic.mark_invite_responded(review, user_id, role, accepted=True)
        messages.success(request, "Thank you — your assignment has been confirmed.")
        return redirect('ear_review_detail', pk=review.pk)

    # Declined — mark invite, remove assignment, and reassign
    ear_logic.mark_invite_responded(review, user_id, role, accepted=False)

    if role == 'supervisor':
        if review.supervisor_id == user_id:
            review.supervisor = None
            review.save(update_fields=['supervisor', 'updated_at'])
            new_person = ear_logic.auto_assign_supervisor(review)
            if new_person and new_person.email:
                ear_logic.notify_assignment(review, new_person, 'supervisor')

    elif role == 'reviewer':
        EARReviewer.objects.filter(review=review, reviewer_id=user_id).delete()
        new_person = ear_logic.auto_assign_reviewer(review)
        if new_person and new_person.email:
            ear_logic.notify_assignment(review, new_person, 'reviewer')

    messages.info(request, "You have declined the assignment. A replacement has been sought.")
    return redirect('ear_review_list')


@login_required
def assembly_project_edit(request, pk):
    ap = get_object_or_404(AssemblyProject, pk=pk)

    # Authorise: superuser or member of this species' assembly team
    allowed = request.user.is_superuser or AssemblyTeam.objects.filter(
        members__user=request.user,
        genometeam__species=ap.species,
    ).exists()

    if not allowed:
        messages.error(request, "You do not have permission to edit this assembly project.")
        return redirect('assembly_project_list')

    if request.method == 'POST':
        status = request.POST.get('status', '').strip()
        note = request.POST.get('note', '').strip()
        genome_size_raw = request.POST.get('genome_size_estimate', '').strip()

        valid_statuses = [c[0] for c in ASSEMBLY_STATUS_CHOICES]
        if status and status in valid_statuses:
            ap.status = status
        if note != ap.note:
            ap.note = note or None
        if genome_size_raw:
            try:
                ap.genome_size_estimate = int(genome_size_raw)
            except ValueError:
                pass
        elif genome_size_raw == '':
            ap.genome_size_estimate = None
        ap.save()
        messages.success(request, f"Assembly project for {ap.species} updated.")

    return redirect('assembly_project_list')


@login_required(login_url='access_denied')
def sequencing_edit(request, pk):
    seq = get_object_or_404(Sequencing, pk=pk)

    allowed = request.user.is_superuser or SequencingTeam.objects.filter(
        members__user=request.user,
        genometeam__species=seq.species,
    ).exists()

    if not allowed:
        messages.error(request, "You do not have permission to edit this sequencing record.")
        return redirect('sequencing_list')

    if request.method == 'POST':
        valid_statuses = [c[0] for c in SEQUENCING_STATUS_CHOICES]
        for field in ('long_seq_status', 'short_seq_status', 'hic_seq_status', 'rna_seq_status'):
            val = request.POST.get(field, '').strip()
            if val and val in valid_statuses:
                setattr(seq, field, val)
        note = request.POST.get('note', '').strip()
        seq.note = note or None
        seq.save()
        messages.success(request, f"Sequencing record for {seq.species} updated.")

    return redirect('sequencing_list')



class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = 'access_denied'
    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'My Dashboard'
        context['pending_invites'] = (
            EARAssignmentInvite.objects
            .filter(user=self.request.user, status='pending')
            .select_related('review__assembly_project__species', 'review__submitted_by')
            .order_by('created_at')
        )
        context['ears_to_review'] = (
            EARReview.objects
            .filter(reviewers=self.request.user, status__in=['submitted', 'in_review'])
            .select_related('assembly_project__species', 'submitted_by')
            .order_by('updated_at')
        )
        context['ears_awaiting_decision'] = (
            EARReview.objects
            .filter(supervisor=self.request.user, status='reviewer_approved')
            .select_related('assembly_project__species', 'submitted_by')
            .order_by('updated_at')
        )
        context['my_submissions'] = (
            EARReview.objects
            .filter(submitted_by=self.request.user)
            .exclude(status__in=['accepted', 'declined'])
            .select_related('assembly_project__species')
            .prefetch_related('reviewers')
            .order_by('updated_at')
        )

        # Reviews where a new PDF was uploaded (by someone else) after the user's last comment
        from django.db.models import Q, F, OuterRef, Subquery
        from status.models import EARPdfVersion, EARComment as _EARComment
        _latest_pdf_subq = EARPdfVersion.objects.filter(
            review=OuterRef('pk'),
        ).exclude(
            uploaded_by=self.request.user,
        ).order_by('-uploaded_at').values('uploaded_at')[:1]
        _latest_comment_subq = _EARComment.objects.filter(
            review=OuterRef('pk'),
            author=self.request.user,
            is_system=False,
        ).order_by('-created_at').values('created_at')[:1]
        context['ear_pdf_updates'] = (
            EARReview.objects
            .filter(Q(supervisor=self.request.user) | Q(reviewers=self.request.user))
            .annotate(
                latest_pdf=Subquery(_latest_pdf_subq),
                latest_comment=Subquery(_latest_comment_subq),
            )
            .filter(latest_pdf__isnull=False)
            .exclude(latest_comment__gte=F('latest_pdf'))
            .distinct()
            .select_related('assembly_project__species', 'submitted_by')
            .order_by('updated_at')
        )
        my_assembly_projects = (
            AssemblyProject.objects
            .filter(species__gt_rel__assembly_team__members__user=self.request.user)
            .select_related('species')
            .prefetch_related('ear_review')
            .distinct()
            .order_by('species__scientific_name')
        )
        # Annotate each project with an EAR flag for the template
        flagged = []
        for ap in my_assembly_projects:
            ear = getattr(ap, 'ear_review', None)
            if ear is None:
                flag = None
            elif ear.status in ('rejected', 'declined'):
                flag = ear.get_status_display()
            else:
                flag = None
            flagged.append({'project': ap, 'ear': ear, 'flag': flag})
        context['my_assembly_projects'] = flagged
        context['my_sequencing_tasks'] = (
            Sequencing.objects
            .filter(species__gt_rel__sequencing_team__members__user=self.request.user)
            .exclude(
                long_seq_status__in=['Done', 'Abandoned'],
                short_seq_status__in=['Done', 'Abandoned'],
                hic_seq_status__in=['Done', 'Abandoned'],
                rna_seq_status__in=['Done', 'Abandoned'],
            )
            .select_related('species')
            .distinct()
            .order_by('species__scientific_name')
        )
        # Context for the edit modals (matches assemblyproject.html / sequencing.html)
        context['assembly_status_choices'] = ASSEMBLY_STATUS_CHOICES
        context['sequencing_status_choices'] = SEQUENCING_STATUS_CHOICES
        context['sequencing_status_fields'] = [
            ('long_seq_status',  'Long-read Status'),
            ('short_seq_status', 'Short-read Status'),
            ('hic_seq_status',   'HiC Status'),
            ('rna_seq_status',   'RNA Status'),
        ]
        if self.request.user.is_superuser:
            from django.conf import settings as django_settings
            from django.utils import timezone
            import datetime
            threshold_days = getattr(django_settings, 'EAR_STUCK_THRESHOLD_DAYS', 7)
            stuck_cutoff = timezone.now() - datetime.timedelta(days=threshold_days)
            active_statuses = ['submitted', 'in_review', 'reviewer_approved']
            context['superuser_overview'] = {
                'open_ears': EARReview.objects.filter(status__in=active_statuses).count(),
                'stuck_ears': EARReview.objects.filter(
                    status__in=active_statuses,
                    updated_at__lt=stuck_cutoff,
                ).count(),
                'stuck_threshold_days': threshold_days,
                'stuck_reviews': (
                    EARReview.objects
                    .filter(status__in=active_statuses, updated_at__lt=stuck_cutoff)
                    .select_related('assembly_project__species')
                    .order_by('updated_at')
                ),
            }
        return context


@login_required
@require_POST
def dashboard_invite_response(request, pk):
    """Accept or decline an EAR assignment invite from the dashboard."""
    from status import ear_review as ear_logic

    invite = get_object_or_404(EARAssignmentInvite, pk=pk, user=request.user, status='pending')
    response = request.POST.get('response')
    review = invite.review

    if response == 'accept':
        ear_logic.mark_invite_responded(review, request.user.pk, invite.role, accepted=True)
        messages.success(request, f"You have accepted the {invite.get_role_display().lower()} assignment for {review.assembly_project.species}.")

    elif response == 'decline':
        ear_logic.mark_invite_responded(review, request.user.pk, invite.role, accepted=False)
        if invite.role == 'supervisor':
            if review.supervisor_id == request.user.pk:
                review.supervisor = None
                review.save(update_fields=['supervisor', 'updated_at'])
                new_person = ear_logic.auto_assign_supervisor(review)
                if new_person and new_person.email:
                    ear_logic.notify_assignment(review, new_person, 'supervisor')
        elif invite.role == 'reviewer':
            EARReviewer.objects.filter(review=review, reviewer=request.user).delete()
            new_person = ear_logic.auto_assign_reviewer(review)
            if new_person and new_person.email:
                ear_logic.notify_assignment(review, new_person, 'reviewer')
        messages.info(request, f"You have declined the assignment. A replacement has been sought.")

    return redirect('dashboard')


def _can_replace_pdf(user, review):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return AssemblyTeam.objects.filter(
        members__user=user,
        genometeam__species=review.assembly_project.species,
    ).exists()


@login_required
def ear_review_replace_pdf(request, pk):
    from status.forms import EARPdfReplaceForm
    from status import ear_review as ear_logic
    from django.db import transaction

    review = get_object_or_404(EARReview, pk=pk)

    if not _can_replace_pdf(request.user, review):
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden()

    if request.method != 'POST':
        return redirect('ear_review_detail', pk=pk)

    form = EARPdfReplaceForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Invalid submission: ' + ' '.join(
            e for errors in form.errors.values() for e in errors
        ))
        return redirect('ear_review_detail', pk=pk)

    note = form.cleaned_data.get('note', '').strip()

    with transaction.atomic():
        review.pdf_versions.update(is_current=False)
        new_version = EARPdfVersion.objects.create(
            review=review,
            file=form.cleaned_data['ear_pdf'],
            uploaded_by=request.user,
            is_current=True,
            note=note,
        )
        review.ear_pdf = new_version.file
        review.save(update_fields=['ear_pdf', 'updated_at'])
        body = 'Replaced the EAR PDF' + (f': {note}' if note else '')
        EARComment.objects.create(
            review=review,
            author=request.user,
            body=body,
            is_system=True,
        )

    ear_logic.notify_pdf_replaced(review, request.user, note)
    messages.success(request, 'EAR PDF replaced successfully.')
    return redirect('ear_review_detail', pk=pk)


def _can_modify_comment(user, comment):
    return (
        user.is_authenticated
        and not comment.is_system
        and not comment.is_deleted
        and comment.author_id == user.id
    )


@login_required
@require_POST
def ear_comment_edit(request, pk):
    """Edit own comment body. Sets edited_at marker."""
    from django.utils import timezone
    comment = get_object_or_404(EARComment, pk=pk)
    if not _can_modify_comment(request.user, comment):
        messages.error(request, "You can't edit this comment.")
        return redirect('ear_review_detail', pk=comment.review_id)
    new_body = request.POST.get('body', '').strip()
    if not new_body:
        messages.error(request, "Comment body is empty.")
        return redirect('ear_review_detail', pk=comment.review_id)
    comment.body = new_body
    comment.edited_at = timezone.now()
    comment.save(update_fields=['body', 'edited_at'])
    messages.success(request, "Comment updated.")
    return redirect(f"{reverse('ear_review_detail', kwargs={'pk': comment.review_id})}#comment-{comment.pk}")


@login_required
@require_POST
def ear_comment_delete(request, pk):
    """Soft-delete own comment (row remains; body hidden in template)."""
    comment = get_object_or_404(EARComment, pk=pk)
    if not _can_modify_comment(request.user, comment):
        messages.error(request, "You can't delete this comment.")
        return redirect('ear_review_detail', pk=comment.review_id)
    comment.is_deleted = True
    comment.save(update_fields=['is_deleted'])
    messages.success(request, "Comment deleted.")
    return redirect('ear_review_detail', pk=comment.review_id)
