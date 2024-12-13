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
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.db.models import Q
from django.db.models import F, Value
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.decorators import method_decorator
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
from django.urls import reverse_lazy
from status.filters import GenomeTeamFilter
from status.filters import OverviewSpeciesFilter
from status.filters import SpeciesFilter
from status.filters import ReadsFilter
from status.filters import AssemblyFilter
from status.filters import SpecimenFilter
from status.filters import SampleFilter
from status.filters import SampleCollectionFilter
from braces.views import GroupRequiredMixin
from django.db.models import OuterRef, Subquery
from django.core.cache import cache
from django.db.models.functions import Coalesce
from django_cron import CronJobBase, Schedule
from datetime import datetime
import requests
import logging
import re
from unicodedata import normalize
from unidecode import unidecode
import yaml
import urllib
from urllib import request

# Get an instance of a logger
# logger = logging.getLogger(__name__)
# import logging

# Create a logger for your app
logger = logging.getLogger('status')

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

def index(request):
    return HttpResponse("Hello, world. You're at the status index.")

class HelpView(TemplateView):
    template_name = 'help.html'
"""     try:
        # Simulate some debug information
        logger.debug("This is a debug message. View executed successfully.")

        # # Simulate a warning
        # if some_condition():
        #     logger.warning("This is a warning message. Something might be off.")

        # # Simulate an error
        # if another_condition():
        #     raise ValueError("This is an error message.")

        # return HttpResponse("View executed successfully.")
    except Exception as e:
        # Log an error message
        logger.error(f"An error occurred: {e}")
        # return HttpResponse("An error occurred.") """
    
    

def home(request):
    centerlabels = []
    waiting = []
    collected = []
    not_collected = []
    sequencing = []
    seq_done = []
    assembling = []
    assembly_done = []
    total_collected = []
    total_not_collected = []
    total_sequencing = []
    total_seq_done = []
    total_assembling = []
    total_assembly_done = []
    total_submitted = []
   # speciesdict = {}
    in_production_set = {'Received', 'Prep', 'Sequencing', 'TopUp', 'Extracted'}
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
        submitted_span = 0
        #.filter(sequencing_rel__long_seq_status='Done')
        queryset = TargetSpecies.objects.filter(gt_rel__sequencing_team=c)
        if (queryset):
            for sp in queryset:
                #assigned_span += sp.genome_size
                if (sp.assembly_rel.status in assembly_done_set):
                        assembly_done_span += sp.genome_size_update
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
        else:
            not_collected.append(0)
            collected.append(0)
            sequencing.append(0)
            seq_done.append(0)
            assembling.append(0)
            assembly_done.append(0)

#### TOTALS


    total_not_collected_span = 0
    total_collected_span = 0
    total_sequencing_span = 0
    total_seq_done_span = 0
    total_assembling_span = 0
    total_assembly_done_span = 0
        #.filter(sequencing_rel__long_seq_status='Done')
    allqueryset = TargetSpecies.objects.all().exclude(goat_target_list_status = None).exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed')

    if (allqueryset):
        for sp in allqueryset:
            #assigned_span += sp.genome_size
            if not sp.genome_size_update:
                sp.genome_size_update = 0;
            if (sp.assembly_rel and sp.assembly_rel.status in assembly_done_set):
                    total_assembly_done_span += sp.genome_size_update
            else:
                if ((sp.assembly_rel.status in in_assembly_set) and (sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                    total_assembling_span += sp.genome_size_update
                else:
                    if ((sp.sequencing_rel.long_seq_status in seq_done_set) and (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                        total_seq_done_span += sp.genome_size_update
                    else: 
                        if ((sp.sequencing_rel.long_seq_status in in_production_set) or (sp.sequencing_rel.hic_seq_status in in_production_set) or (sp.sequencing_rel.long_seq_status in seq_done_set) or (sp.sequencing_rel.hic_seq_status in seq_done_set)):
                            total_sequencing_span += sp.genome_size_update
                        else:
                            if ((sp.goat_sequencing_status == 'sample_collected') or (sp.goat_sequencing_status == 'sample_acquired')):
                                total_collected_span += sp.genome_size_update
                            else:
                                total_not_collected_span += sp.genome_size_update

                         
    # goat_sequencing_status
    total_not_collected_span = total_not_collected_span/1000000000
    total_collected_span = total_collected_span/1000000000
    total_sequencing_span = total_sequencing_span/1000000000
    total_seq_done_span = total_seq_done_span/1000000000
    total_assembling_span = total_assembling_span/1000000000
    total_assembly_done_span = total_assembly_done_span/1000000000
            
    # messages.info(request, 'centers: ' + str(centerlabels)) 
    # messages.info(request, 'not_collected: ' + str(not_collected)) 
    # messages.info(request, 'collected: ' + str(collected)) 
    # messages.info(request, 'sequencing: '+ str(sequencing))  
    # messages.info(request, 'seq_done: '+ str(seq_done)) 
    # messages.info(request, 'assembling: '+ str(assembling))  
    # messages.info(request, 'assembly_done: '+ str(assembly_done))  
    # messages.info(request, 'total_not_collected: '+ str(total_not_collected_span))  
    # messages.info(request, 'total_collected: '+ str(total_collected_span)) 
    # messages.info(request, 'total_sequencing: '+ str(total_sequencing_span))  
    # messages.info(request, 'total_seq_done: '+ str(total_seq_done_span)) 
    # messages.info(request, 'total_assembling: '+ str(total_assembling_span)) 
    # messages.info(request, 'total_assembly_done: '+ str(total_assembly_done_span))  
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
    })

class SuccessView(TemplateView):
    template_name = 'success.html'

# Create your views here.
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
        context['build_page_title'] = 'ERGA-GTC Species'
        return context
    
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
        context['build_page_title'] = 'ERGA-GTC GoaT List'
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
    # permission_required = "resistome.view_sample"
    login_url = "access_denied"
    model = TargetSpecies
    table_class = OverviewTable
    template_name = 'overview.html'
    filterset_class = OverviewSpeciesFilter
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    def get_context_data(self, *args, **kwargs):
        data = super(OverView, self).get_context_data(*args, **kwargs)
        data['build_page_title'] = 'ERGA-GTC OverView'
        return data
    
    def get_queryset(self):
        return TargetSpecies.objects.exclude(goat_target_list_status = None).exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = '').exclude(goat_target_list_status = 'removed').exclude(goat_sequencing_status = 'none').exclude(genome_size = None).order_by('-gss_rank','-assembly_rel__assembly_rank','collection_rel__copo_status','taxon_kingdom','taxon_phylum','taxon_class','taxon_order','taxon_family','taxon_genus','scientific_name')
        #return TargetSpecies.objects.exclude(goat_sequencing_status = None).exclude(goat_sequencing_status = '')

@login_required
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
    template_name = 'assemblyproject.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Assembly Status'
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Assemblies'
        return context
    def get_queryset(self):
        return Assembly.objects.filter(chromosome_level=True).exclude(type='Hap2').exclude(type='Endosymbiont').exclude(type='Alternate').exclude(type='MT').exclude(type='Chloroplast')
    #     queryset = super(AssemblyListView, self).get_queryset()
    #     if 'gca' in self.request.GET:
    #         queryset = queryset.filter(gca=self.request.GET['gca'])
    #         return queryset
    #     else:
    #         return AssemblyProject.objects.all()


@login_required
def assembly_pipeline_detail(request, pk=None):
    pipeline = AssemblyPipeline.objects.get(pk=pk)
    context = {"pipeline": pipeline
               }
    response = render(request, "assembly_pipeline_detail.html", context)
    return response

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
        context['build_page_title'] = 'ERGA-GTC Sample Collection'
        return context
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
        context['build_page_title'] = 'ERGA-GTC Specimens'
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
        context['build_page_title'] = 'ERGA-GTC GoaT Samples'
        return context

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
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Sequencing Status'
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
        context['build_page_title'] = 'ERGA-GTC Sequencing'
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
        if 'project' in self.request.GET:
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Runs'
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
        if 'project' in self.request.GET:
            queryset = queryset.filter(project=self.request.GET['project'])
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC ENA Runs'
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
        context['build_page_title'] = 'ERGA-GTC Read Data'
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
        context['build_page_title'] = 'ERGA-GTC Read Data'
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
        context['build_page_title'] = 'ERGA-GTC Annotations'
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
        context['build_page_title'] = 'ERGA-GTC Community Annotations'
        return context
    def get_queryset(self):
        return CommunityAnnotation.objects.exclude(species__goat_target_list_status = None).exclude(species__goat_target_list_status = 'none').exclude(species__goat_target_list_status = '').exclude(species__goat_target_list_status = 'removed').exclude(species__goat_sequencing_status = 'none')


class AccessDeniedView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Access Denied'
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
        context['build_page_title'] = 'ERGA-GTC Genome Teams'
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
        context['build_page_title'] = 'ERGA-GTC Authors'
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
        context['build_page_title'] = 'ERGA-GTC Edit Profile'
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
        context['build_page_title'] = 'ERGA-GTC Log'
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
        context['build_page_title'] = 'ERGA-GTC Species Log'
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
        context['build_page_title'] = 'ERGA-GTC Upload Species List'
        return context

    def form_valid(self, form):
        gtls_options = ['waiting_list', 'none', 'long_list', 'other_priority', 'family_representative','removed']
        gss_options = ['none', 'in_collection', 'sample_collected', 'sample_acquired', 'data_generation', 'in_assembly', 'insdc_open', 'publication_available' ]
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
               'build_page_title':'ERGA-GTC Recipe'
               }
    response = render(request, "recipe_detail.html", context)
    return response

@login_required
def sample_detail(request, pk=None):
    sample = Sample.objects.get(pk=pk)
    site_url = settings.DEFAULT_DOMAIN
    context = {"sample": sample,
               "site_url": site_url,
               'build_page_title':'ERGA-GTC Sample'
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
            
class UpdateSamplesCronJob(CronJobBase):
    RUN_EVERY_MINS = 720 # every 3 hours
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'status.update_samples_cron_job'    # a unique code
    

    def do(self):
        def strip_blanks(string_list):
            endtrimmed = [re.sub(r'\s+$', '', name) for name in string_list]
            both_trimmed = [re.sub(r'^\s+', '', name) for name in endtrimmed]
            return both_trimmed
        now = datetime.now() # current date and time
        date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
        logger.debug(date_time + ": Executing UpdateSamplesCronJob.")
        logging.getLogger("requests").setLevel(logging.WARNING)
        urllib3_logger = logging.getLogger('urllib3')
        urllib3_logger.setLevel(logging.CRITICAL)
        copo_url="https://copo-project.org/api"
        species_qs = TargetSpecies.objects.all().values("taxon_id","goat_target_list_status")    
        for sp in species_qs:
            if sp['taxon_id'] is not None and sp["goat_target_list_status"] != "removed":
                # if sp['taxon_id'] is not '269343':
                #     continue
                
                # #print('taxon_id: '+ sp['taxon_id']) 
                tid = sp.get('taxon_id')
                #print(copo_url+"/sample/sample_field/TAXON_ID/"+tid)
                copo_taxid_json = []
                num_samples = 0
                #species_copo_status = 'Not submitted'
                try:
                    copo_taxid_response = requests.get(copo_url+"/sample/sample_field/TAXON_ID/"+tid)
                    copo_taxid_response.raise_for_status()
                    #print(copo_taxid_response)
                    #print(copo_taxid_response.json())
                    copo_taxid_json = copo_taxid_response.json()
                    #print(json_resp["status"])
                    #print(str(copo_taxid_json["number_found"])+' samples found for '+tid)
                    num_samples = copo_taxid_json.get("number_found")
                    data = copo_taxid_json.get("data")
                except requests.exceptions.HTTPError as error:
                    continue
                    #print(error)
                if num_samples > 0:
                    for copo_record in data:
                        copo_id = copo_record.get('copo_id')
                        logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + ": UpdateSamplesCronJob: getting copo_id "+copo_id+".")
                        #print(copo_id)
                        copo_sample_json = []
                        num_found = 0
                        try:
                            copo_sample_response = requests.get(copo_url+"/sample/copo_id/"+copo_record['copo_id']+'/')
                        except requests.exceptions.HTTPError as error:
                            continue
                            #print(error)
                        if not copo_sample_response:
                            continue
                        copo_sample_json = copo_sample_response.json()
                        num_found = copo_sample_json.get('number_found')
                        sample_data_all = copo_sample_json.get('data')
                        if num_found > 0:
                            if num_found > 1:
                                sys.exit("more than one copo_record per copo id !!!")
                            status = ''
                            updated_species = False
                            sample_data = sample_data_all[0]
                            if 'BARCODING' in sample_data['PURPOSE_OF_SPECIMEN']:
                                continue
                            if 'RESEQUENCING' in sample_data['PURPOSE_OF_SPECIMEN']:
                                continue
                            tolid = sample_data.get('public_name')
                            #print(tolid)
                            taxid = sample_data.get('TAXON_ID')
                            tol_project = sample_data.get('tol_project')
                            associated_tol_project = sample_data.get('associated_tol_project')
                            primary_biogenome_project = sample_data.get('PRIMARY_BIOGENOME_PROJECT')
                            if primary_biogenome_project is None:
                                continue
                            if ('ERGA-BGE' not in primary_biogenome_project and 
                                'ERGA' not in tol_project and
                                'BGE' not in tol_project and
                                'ERGA' not in associated_tol_project and
                                'BGE' not in associated_tol_project):
                                continue
                            #print(tolid +'|' +copo_id)
                            copo_status = sample_data.get('status')
                            specimen_id = sample_data.get('SPECIMEN_ID')
                            if 'pending' in copo_status:
                                status = 'pending'
                            else:
                                status = copo_status
                            if not ((status == 'pending') or (status == 'accepted') or (status == "rejected")):
                                continue
                            tolid_prefix = tolid
                            tolid_prefix = re.sub(r'\d+$', '', tolid)
                            #print(tolid_prefix)
                            sample_accession = sample_data.get('biosampleAccession')
                            species = TargetSpecies.objects.get(taxon_id=tid)
                            species_copo_status = species.copo_status
                            if tolid_prefix != species.tolid_prefix:
                                species.tolid_prefix = tolid_prefix
                                updated_species = True
                            #get sample_collection -- not sure if needed. it would return multiple records now
                            specimen_record, _ = Specimen.objects.get_or_create(tolid=tolid) # if doesn't exist create it
                            collection_qs = SampleCollection.objects.filter(species=species)
                            if (len(collection_qs) == 1): #don't have a way to match up collection with specimen, yet. can do some matching of names and countries...
                                specimen_record.collection = collection_qs[0] 
                            specimen_record.tolid = tolid
                            specimen_record.specimen_id = specimen_id
                            specimen_record.species = species
                            specimen_record.tissue_removed_for_biobanking = True if sample_data.get('TISSUE_REMOVED_FOR_BIOBANKING') == 'Y' else False
                            specimen_record.tissue_voucher_id_for_biobanking = sample_data.get('TISSUE_VOUCHER_ID_FOR_BIOBANKING')
                            specimen_record.proxy_tissue_voucher_id_for_biobanking = sample_data.get('PROXY_TISSUE_VOUCHER_ID_FOR_BIOBANKING')
                            specimen_record.tissue_for_biobanking = sample_data.get('TISSUE_FOR_BIOBANKING')
                            specimen_record.dna_removed_for_biobanking = True if sample_data.get('DNA_REMOVED_FOR_BIOBANKING') == 'Y' else False
                            specimen_record.dna_voucher_id_for_biobanking = sample_data.get('DNA_VOUCHER_ID_FOR_BIOBANKING')
                            specimen_record.voucher_id = sample_data.get('VOUCHER_ID')
                            specimen_record.proxy_voucher_id = sample_data.get('PROXY_VOUCHER_ID')
                            specimen_record.voucher_link = sample_data.get('VOUCHER_LINK')
                            specimen_record.proxy_voucher_link = sample_data.get('PROXY_VOUCHER_LINK')
                            specimen_record.voucher_institution = sample_data.get('VOUCHER_INSTITUTION')
                            if len(sample_data.get('sampleDerivedFrom'))>1:
                                specimen_record.biosampleAccession = sample_data.get('sampleDerivedFrom')
                            elif len(sample_data.get('sampleSameAs'))>1:
                                specimen_record.biosampleAccession = sample_data.get('sampleSameAs')
                            #print(sample_data)
                            #sys.exit()
                            specimen_record.save()
                            sample_record, _ = Sample.objects.get_or_create(copo_id=copo_id) ### Check to see that only one sample is returned. There's a case with two
                            sample_record.biosampleAccession = sample_data.get('biosampleAccession')
                            sample_record.species = species
                            sample_record.gal = sample_data.get('GAL')
                            sample_record.barcode = ''
                            sample_record.collector_sample_id = sample_data.get('COLLECTOR_SAMPLE_ID')
                            sample_record.copo_date = sample_data.get('time_updated')
                            sample_record.copo_status = sample_data.get('status')
                            sample_record.purpose_of_specimen = sample_data.get('PURPOSE_OF_SPECIMEN')
                            sample_record.tube_or_well_id = sample_data.get('TUBE_OR_WELL_ID')
                            sample_record.gal_sample_id = sample_data.get('GAL_SAMPLE_ID')
                            sample_record.sampleDerivedFrom = sample_data.get('sampleDerivedFrom')
                            sample_record.sampleSameAs = sample_data.get('sampleSameAs')
                            sample_record.specimen = specimen_record
                            sample_record.save()

                            #update genome team with sequencing team
                            seq_team_name = sample_data.get('GAL')
                            seq_team_name_ascii = unidecode(seq_team_name)
                            assign_center = 0
                            if assign_center:
                                if (seq_team_name is not None) and (seq_team_name != 'Other_ERGA_Associated_GAL'):
                                    seqteam = SequencingTeam.objects.filter(gal_name=seq_team_name_ascii).first()
                                    if seqteam is not None:
                                        #print(seqteam)
                                        gt, _ = GenomeTeam.objects.get_or_create(species=species)
                                        if gt is not None:
                                            gt.sequencing_team = seqteam
                                            gt.save()
                                    else:
                                        newseqteam = SequencingTeam.objects.create(name=seq_team_name_ascii,gal_name=seq_team_name_ascii)
                                        newseqteam.save()
                                        gt, _ = GenomeTeam.objects.get_or_create(species=species)
                                        if gt is not None:
                                            gt.sequencing_team = newseqteam
                                            gt.save()

                            #$from_mani_query  = "$erga_status_url/from_manifest/?specimen=".$specimen_pk;
                            from_manifest_record, _ = FromManifest.objects.get_or_create(specimen=specimen_record)
                            collector_names = []
                            collector_affiliations = []
                            collector_affiliations_records = []
                            collector_orcids = []
                            collected_by_string = sample_data.get('COLLECTED_BY')
                            if collected_by_string is not None:
                                from_manifest_record.sample_collectors = collected_by_string
                                collector_names = strip_blanks(collected_by_string.split('|'))
                                #print(collector_names)
                            collector_affiliation_string = sample_data.get('COLLECTOR_AFFILIATION')
                            if collector_affiliation_string is not None:
                                from_manifest_record.sample_collector_affiliations = collector_affiliation_string
                                collector_affiliations = strip_blanks(collector_affiliation_string.split('|'))
                                #print(collector_affiliations)
                                for aff in collector_affiliations:
                                    affrecord, _ = Affiliation.objects.get_or_create(affiliation=aff)
                                    collector_affiliations_records.append(affrecord)
                            collector_orcid_string = sample_data.get('COLLECTOR_ORCID_ID')
                            if collector_orcid_string is not None:
                                from_manifest_record.sample_collector_orcids = collector_orcid_string
                                collector_orcids = strip_blanks(collector_orcid_string.split('|'))
                                #print(collector_orcids)
                            ### Now add each person
                            for i in range(len(collector_names)):
                                #print(i)
                                if i >= len(collector_affiliations_records):
                                    collector_affiliations_records.append(None)
                                if i >= len(collector_orcids):
                                    collector_orcids.append(None)
                                people = Person.objects.filter(name=collector_names[i])
                                if (len(people)>0):
                                    for p in people:
                                        if collector_affiliations_records[i] is not None:
                                            if Affiliation.objects.filter(pk=collector_affiliations_records[i].pk).exists():
                                                pass
                                            else:
                                                p.affiliation.add(collector_affiliations_records[i])
                                                # add person to from_manifest
                                        if from_manifest_record.collector.filter(pk=p.pk).exists():
                                            pass
                                        else:
                                            from_manifest_record.collector.add(p)
                                else:
                                    person, _ = Person.objects.get_or_create(name=collector_names[i],orcid=collector_orcids[i])
                                    if collector_affiliations_records[i] is not None:
                                        person.affiliation.add(collector_affiliations_records[i])
                                        person.save()
                                    # add person to from_manifest
                                    if from_manifest_record.preserver.filter(pk=person.pk).exists():
                                        pass
                                    else:
                                        from_manifest_record.preserver.add(person)


                            identifier_names = []
                            identifier_affiliations = []
                            identifier_affiliations_records = []
                            identified_by_string = sample_data.get('IDENTIFIED_BY')
                            if identified_by_string is not None:
                                from_manifest_record.sample_identifiers = identified_by_string
                                identifier_names = strip_blanks(identified_by_string.split('|'))
                                #print(identifier_names)
                            identifier_affiliation_string = sample_data.get('IDENTIFIER_AFFILIATION')
                            if identifier_affiliation_string is not None:
                                from_manifest_record.sample_identifier_affiliations = identifier_affiliation_string
                                identifier_affiliations = strip_blanks(identifier_affiliation_string.split('|'))
                                #print(identifier_affiliations)
                                for aff in identifier_affiliations:
                                    affrecord, _ = Affiliation.objects.get_or_create(affiliation=aff)
                                    identifier_affiliations_records.append(affrecord)
                            ### Now add each person
                            for i in range(len(identifier_names)):
                                if i >= len(identifier_affiliations_records):
                                    identifier_affiliations_records.append(None)
                                people = Person.objects.filter(name=identifier_names[i])
                                if (len(people)>0):
                                    for p in people:
                                        if identifier_affiliations_records[i] is not None:
                                            if Affiliation.objects.filter(pk=identifier_affiliations_records[i].pk).exists():
                                                pass
                                            else:
                                                p.affiliation.add(identifier_affiliations_records[i])
                                                # add person to from_manifest
                                        if from_manifest_record.identifier.filter(pk=p.pk).exists():
                                            pass
                                        else:
                                            from_manifest_record.identifier.add(p)
                                else:
                                    person, _ = Person.objects.get_or_create(name=identifier_names[i])
                                    if identifier_affiliations_records[i] is not None:
                                        person.affiliation.add(identifier_affiliations_records[i])
                                        person.save()
                                    # add person to from_manifest
                                    if from_manifest_record.preserver.filter(pk=person.pk).exists():
                                        pass
                                    else:
                                        from_manifest_record.preserver.add(person)

                            coordinator_names = []
                            coordinator_affiliations = []
                            coordinator_affiliations_records = []
                            coordinator_orcids = []
                            coordinated_by_string = sample_data.get('SAMPLE_COORDINATOR')
                            if coordinated_by_string is not None:
                                from_manifest_record.sample_coordinators = coordinated_by_string
                                coordinator_names = strip_blanks(coordinated_by_string.split('|'))
                                #print(coordinator_names)
                            coordinator_affiliation_string = sample_data.get('SAMPLE_COORDINATOR_AFFILIATION')
                            if coordinator_affiliation_string is not None:
                                from_manifest_record.sample_coordinators_affiliations = coordinator_affiliation_string
                                coordinator_affiliations = strip_blanks(coordinator_affiliation_string.split('|'))
                                #print(coordinator_affiliations)
                                for aff in coordinator_affiliations:
                                    affrecord, _ = Affiliation.objects.get_or_create(affiliation=aff)
                                    coordinator_affiliations_records.append(affrecord)
                            coordinator_orcid_string = sample_data.get('SAMPLE_COORDINATOR_ORCID_ID')
                            if coordinator_orcid_string is not None:
                                from_manifest_record.sample_coordinators_orcids = coordinator_orcid_string
                                coordinator_orcids = strip_blanks(coordinator_orcid_string.split('|'))
                                #print(coordinator_orcids)
                            ### Now add each person
                            for i in range(len(coordinator_names)):
                                if i >= len(coordinator_affiliations_records):
                                    coordinator_affiliations_records.append(None)
                                if i >= len(coordinator_orcids):
                                    coordinator_orcids.append(None)
                                people = Person.objects.filter(name=coordinator_names[i])
                                if (len(people)>0):
                                    for p in people:
                                        if coordinator_affiliations_records[i] is not None:
                                            if Affiliation.objects.filter(pk=coordinator_affiliations_records[i].pk).exists():
                                                pass
                                            else:
                                                p.affiliation.add(coordinator_affiliations_records[i])
                                            # add person to from_manifest
                                        if from_manifest_record.coordinator.filter(pk=p.pk).exists():
                                            pass
                                        else:
                                            from_manifest_record.coordinator.add(p)
                                else:
                                    person, _ = Person.objects.get_or_create(name=coordinator_names[i],orcid=coordinator_orcids[i])
                                    if coordinator_affiliations_records[i] is not None:
                                        person.affiliation.add(coordinator_affiliations_records[i])
                                        person.save()
                                    # add person to from_manifest
                                    if from_manifest_record.preserver.filter(pk=person.pk).exists():
                                        pass
                                    else:
                                        from_manifest_record.preserver.add(person)

                            preserver_names = []
                            preserver_affiliations = []
                            preserver_affiliations_records = []
                            preserved_by_string = sample_data.get('PRESERVED_BY')
                            if preserved_by_string is not None:
                                from_manifest_record.sample_preservers = preserved_by_string
                                preserver_names = strip_blanks(preserved_by_string.split('|'))
                                #print(preserver_names)
                            preserver_affiliation_string = sample_data.get('PRESERVER_AFFILIATION')
                            if preserver_affiliation_string is not None:
                                from_manifest_record.sample_preserver_affiliations = preserver_affiliation_string
                                preserver_affiliations = strip_blanks(preserver_affiliation_string.split('|'))
                                #print(preserver_affiliations)
                                for aff in preserver_affiliations:
                                    affrecord, _ = Affiliation.objects.get_or_create(affiliation=aff)
                                    preserver_affiliations_records.append(affrecord)
                            ### Now add each person
                            for i in range(len(preserver_names)):
                                if i >= len(preserver_affiliations_records):
                                    preserver_affiliations_records.append(None)
                                people = Person.objects.filter(name=preserver_names[i])
                                if (len(people)>0):
                                    for p in people:
                                        if preserver_affiliations_records[i] is not None:
                                            if Affiliation.objects.filter(pk=preserver_affiliations_records[i].pk).exists():
                                                pass
                                            else:
                                                p.affiliation.add(preserver_affiliations_records[i])
                                                # add person to from_manifest
                                        if from_manifest_record.preserver.filter(pk=p.pk).exists():
                                            pass
                                        else:
                                            from_manifest_record.preserver.add(p)
                                else:
                                    person, _ = Person.objects.get_or_create(name=preserver_names[i])
                                    if preserver_affiliations_records[i] is not None:
                                        person.affiliation.add(preserver_affiliations_records[i])
                                        person.save()
                                    # add person to from_manifest
                                    if from_manifest_record.preserver.filter(pk=person.pk).exists():
                                        pass
                                    else:
                                        from_manifest_record.preserver.add(person)

                            best_copo_status = 'rejected'
                            if 'REFERENCE_GENOME' in sample_data.get('PURPOSE_OF_SPECIMEN'):
                                #if species.copo_status != 'accepted':
                                if status == 'accepted':
                                    species.copo_status = 'Accepted'
                                    best_copo_status = 'accepted'
                                    updated_species = True
                                if status == 'pending':
                                    if best_copo_status != 'accepted':
                                        species.copo_status = 'Pending'
                                        best_copo_status = 'pending'
                                        updated_species = True
                                if status == 'rejected':
                                    if best_copo_status == 'rejected':
                                        species.copo_status = 'Rejected'
                                        updated_species = True

                            if updated_species:
                                species.save() 

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
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                #print(f"Failed to fetch data: {response.status_code}")
                return None
            
        data = fetch_repo_tree(owner, repo, branch)
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
            logger.debug(datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + "FetchEARsCronJob: "+ ear_yaml)

            EAR_pdf = regular_url_prefix + pdf
            #print(ear_yaml['Species'])
            assembly_project= AssemblyProject.objects.all().filter(species__scientific_name=ear_yaml['Species']).first()
            if assembly_project:
                #print(assembly_project)
                assembly_object = Assembly.objects.filter(project=assembly_project).first()
                if assembly_object is None:
                    assembly_object = Assembly.objects.create(project=assembly_project)
                #print('assmebly object: ' + str(assembly_object.project))
                for m in ear_yaml['Metrics']:
                    #print(m)
                    if re.match(r'^Pre-curation',m):
                        continue
                    if m == 'Curated hap1':
                        assembly_object.type = 'Hap1'
                    elif m == 'Curated pr':
                        assembly_object.type = 'Primary'
                    elif m == 'Curated collapsed':
                        assembly_object.type = 'Primary'
                    if ear_yaml['Metrics'][m].get('Total bp'):
                        assembly_object.span = re.sub(r',','',ear_yaml['Metrics'][m]['Total bp'])
                    if ear_yaml['Metrics'][m].get('Scaffold N50'):
                        assembly_object.scaffold_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Scaffold N50'])
                    if ear_yaml['Metrics'][m].get('Contig N50'):
                        assembly_object.contig_n50 = re.sub(r',','',ear_yaml['Metrics'][m]['Contig N50'])
                    if ear_yaml['Metrics'][m].get('QV'):
                        assembly_object.qv = ear_yaml['Metrics'][m]['QV']
                    if ear_yaml['BUSCO'].get('ver') is not None and re.search(r'^\d',ear_yaml['BUSCO']['ver']):
                        busco_version = ear_yaml['BUSCO']['ver']
                        bv, created = BUSCOversion.objects.get_or_create(version=busco_version)
                        assembly_object.busco_version = bv
                    if ear_yaml['BUSCO'].get('lineage') is not None and re.search(r'odb',ear_yaml['BUSCO']['lineage']):
                        busco_db = ear_yaml['BUSCO']['lineage']
                        bdb, created = BUSCOdb.objects.get_or_create(db=busco_db)
                        assembly_object.busco_db = bdb
                    if (ear_yaml['Metrics'][m].get('BUSCO sing.')):
                        #print('making busco string')
                        busco_s = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO sing.'])
                        busco_d = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO dupl.'])
                        busco_f = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO frag.'])
                        busco_m = re.sub(r'%','',ear_yaml['Metrics'][m]['BUSCO miss.'])
                        assembly_object.busco  = 'C:{complete:.1f}%[S:{single:.1f}%,D:{duplicate:.1f}%],F:{fragmented:.1f}%,M:{missing:.1f}%'.format(complete = float(busco_s)+float(busco_d), single = float(busco_s), duplicate = float(busco_d), fragmented = float(busco_f), missing = float(busco_m))
                assembly_object.report = EAR_pdf
                assembly_object.save()

