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
from status.forms import NewSpeciesForm
from status.forms import NewSpeciesListForm
from django.urls import reverse_lazy
from status.filters import GenomeTeamFilter
from status.filters import TargetSpeciesFilter
from braces.views import GroupRequiredMixin
from django.db.models import OuterRef, Subquery

# Get an instance of a logger
logger = logging.getLogger(__name__)


class AffiliationCreateView(CreatePopupMixin, CreateView):
    model = Affiliation
    template_name = 'affiliation_form.html'
    fields = ['affiliation']

def index(request):
    return HttpResponse("Hello, world. You're at the status index.")

# class HomeView(TemplateView):
#     template_name = 'index.html'

def home(request):
    centerlabels = []
    waiting = []
    collected = []
    not_collected = []
    sequencing = []
    seq_done = []
    assembling = []
    assembly_done = []
    submitted = []
   # speciesdict = {}
    in_production_set = {'Received', 'Prep', 'Sequencing', 'TopUp', 'Extracted'}
    seq_done_set = {'Done', 'Submitted'}
    in_assembly_set = {'Issue','Assembling', 'Contigs','Scaffolding','Scaffolds','Curating','Done','UnderReview'}
    assembly_done_set = {'Approved','Submitted'}

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
                        assembly_done_span += sp.genome_size
                else:
                    if (sp.assembly_rel.status in in_assembly_set):
                        assembling_span += sp.genome_size
                    else:
                        if (sp.sequencing_rel.long_seq_status in seq_done_set and sp.sequencing_rel.hic_seq_status in seq_done_set):
                            seq_done_span += sp.genome_size
                        else: 
                            if (sp.sequencing_rel.long_seq_status in in_production_set or sp.sequencing_rel.long_seq_status in seq_done_set):
                                sequencing_span += sp.genome_size
                            else:
                                if (sp.goat_sequencing_status == 'sample_collected' or sp.goat_sequencing_status == 'sample_acquired'):
                                    collected_span += sp.genome_size
                                else:
                                    not_collected_span += sp.genome_size

                         
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

    return render(request, 'index.html', {
        'centers': centerlabels,
        'not_collected': not_collected,  
        'collected': collected,
        'sequencing': sequencing,
        'seq_done': seq_done,
        'assembling': assembling,
        'assembly_done': assembly_done
    })

class SuccessView(TemplateView):
    template_name = 'success.html'

# Create your views here.
class TargetSpeciesListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
    model = TargetSpecies
    table_class = TargetSpeciesTable
    template_name = 'targetspecies.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Species'
        return context
    
    def get_queryset(self):
        return TargetSpecies.objects.exclude(goat_target_list_status = None).exclude(goat_target_list_status = '')
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
        #queryset = queryset.filter(pk=self.request.GET['project'])
        if self.request.method == 'GET' and 'task' in self.request.GET: #self.request.GET['task'] is not None:
            species_ids = SampleCollection.objects.filter(task=self.request.GET['task']).values_list("species", flat=True)
            return TargetSpecies.objects.exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = 'waiting_list').exclude(goat_target_list_status = 'removed').filter(id__in=species_ids)
        else:
            return TargetSpecies.objects.exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = 'waiting_list').exclude(goat_target_list_status = 'removed')

class OverView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
    model = TargetSpecies
    table_class = OverviewTable
    template_name = 'overview.html'
    filterset_class = TargetSpeciesFilter
    export_formats = ['csv', 'tsv','xlsx','json']
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 1000}
    def get_context_data(self, *args, **kwargs):
        data = super(OverView, self).get_context_data(*args, **kwargs)
        data['build_page_title'] = 'ERGA-GTC OverView'
        return data
    
    def get_queryset(self):
        return TargetSpecies.objects.exclude(goat_target_list_status = None).exclude(goat_target_list_status = 'none').exclude(goat_target_list_status = '').exclude(goat_sequencing_status = 'none').order_by('goat_sequencing_status','collection_rel__copo_status','taxon_kingdom','taxon_phylum','taxon_class','taxon_order','taxon_family','taxon_genus','scientific_name')
        #return TargetSpecies.objects.exclude(goat_sequencing_status = None).exclude(goat_sequencing_status = '')

#@login_required
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

@permission_required("status.person_detail", login_url='access_denied')
def person_detail(request, pk=None):
    person = Person.objects.get(pk=pk)
    context = {"person": person
               }
    response = render(request, "person_detail.html", context)
    return response

class AssemblyProjectListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    #login_url = "access_denied"
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

class AssemblyListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    #login_url = "access_denied"
    model = Assembly
    table_class = AssemblyTable
    template_name = 'assembly.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Assemblies'
        return context

#@login_required
def assembly_pipeline_detail(request, pk=None):
    pipeline = AssemblyPipeline.objects.get(pk=pk)
    context = {"pipeline": pipeline
               }
    response = render(request, "assembly_pipeline_detail.html", context)
    return response

class SampleCollectionListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
    model = SampleCollection
    table_class = SampleCollectionTable
    template_name = 'collection.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Sample Collection'
        return context
    
class SpecimenListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Specimen
    table_class = SpecimenTable
    #filterset_class = SpecimenFilter
    template_name = 'specimens.html'
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Specimens'
        return context
    
    def get_queryset(self):
        #self.id = get_object_or_404(Specimen, pk=self.kwargs['id'])
        if 'id' in self.kwargs:
            return Specimen.objects.filter(pk=self.kwargs['id'])
        if 'collection' in self.kwargs:
            return Specimen.objects.filter(collection=self.kwargs['collection'])
    
class SampleListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Sample
    table_class = SampleTable
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
    
class SequencingListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
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

class SequencingDetailView(DetailView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
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

class RunListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = Run
    table_class = RunTable
    template_name = 'runs.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Runs'
        return context
    
class ReadsListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
    model = Reads
    table_class = ReadsTable
    template_name = 'reads.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Read Data'
        return context
    
    def get_queryset(self):
        queryset = super(ReadsListView, self).get_queryset()
        queryset = queryset.annotate(ont_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='ONT')),
                                     ont_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='ONT'))/(F("project__species__genome_size")),
                                     hifi_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiFi')),
                                     hifi_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiFi'))/(F("project__species__genome_size")),
                                     short_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='Illumina')),
                                     short_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='Illumina'))/(F("project__species__genome_size")),
                                     hic_yield=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiC')),
                                     hic_cov=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='HiC'))/(F("project__species__genome_size")),
                                     rnaseq_pe=Sum("run_set__seq_yield",filter=Q(run_set__read_type__startswith='RNA')),
                                     )
        return queryset
    
class CurationListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
    model = Curation
    table_class = CurationTable
    template_name = 'curation.html'
    #filterset_class = SpeciesFilter
    table_pagination = {"per_page": 100}
    export_formats = ['csv', 'tsv','xlsx','json']

class AnnotationListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    #login_url = "access_denied"
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

class CommunityAnnotationListView(ExportMixin, SingleTableMixin, FilterView): #LoginRequiredMixin, 
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
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

class NewSpeciesView(LoginRequiredMixin, FormView):
    login_url = "access_denied"
    model = TargetSpecies
    fields = ['taxon_ids']
    template_name = 'status/new_species_form.html'
    form_class = NewSpeciesForm
    success_url = reverse_lazy("add_species") #reverse_lazy('success')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['build_page_title'] = 'ERGA-GTC Add Species'
        return context
    
    def form_valid(self, form):
        # form.instance.tag = "bge"
        form.save()
        messages.success(self.request, 'Species added successfully. Add another?')  
        #return HttpResponseRedirect(self.request.path_info)
        return super(NewSpeciesView, self).form_valid(form)

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
                        try:
                            targetspecies = TargetSpecies.objects.get(taxon_id=taxid)
                        except TargetSpecies.DoesNotExist:
                            targetspecies, _ = TargetSpecies.objects.get_or_create(
                                taxon_id=taxid
                            )
                        #messages.info(self.request, 'taxon_id: ' + row['taxon_id'])
                        if 'original_species' in row:
                            targetspecies.listed_species = row['original_species'] or None
                        if 'scientific_name' in row:
                            targetspecies.scientific_name = row['scientific_name'] or None
                        if 'tolid_prefix' in row:
                            targetspecies.tolid_prefix = row['tolid_prefix'] or None
                        if 'chromosome_number' in row:
                            targetspecies.chromosome_number = row['chromosome_number'] or None
                        if 'haploid_number' in row:
                            targetspecies.haploid_number = row['haploid_number'] or None
                        if 'ploidy' in row:
                            targetspecies.ploidy = row['ploidy'] or None
                        if 'c_value' in row:
                            targetspecies.c_value = row['c_value'] or None
                        if 'genome_size' in row:
                            targetspecies.genome_size = round(float(row['genome_size'])) or None
                        if 'synonym' in row:
                            targetspecies.synonym = row['synonym'] or None
                        if 'goat_target_list_status' in row:
                            #messages.info(self.request, 'gtls: ' + row['goat_target_list_status'])
                            if (row['goat_target_list_status'] not in gtls_options):
                                messages.info(self.request, "Value " + row['goat_target_list_status'] + " not allowed for goat_target_list_status: please fix and try again.")
                            targetspecies.goat_target_list_status = row['goat_target_list_status'] or None
                        else:
                            messages.info(self.request, "No goat_target_list_status field found: please fix and try again.")
                        if 'goat_sequencing_status' in row:
                            #messages.info(self.request, 'gss: ' + row['goat_sequencing_status'])
                            gss = row['goat_sequencing_status']
                            if gss and gss.strip():
                                if (gss not in gss_options):
                                    messages.info(self.request, "Value " + gss + " not allowed for goat_sequencing_status: please fix and try again.")
                                    break
                                if ( gss == "remove" or (targetspecies.goat_sequencing_status == 'none' or targetspecies.goat_sequencing_status == 'in_collection' or targetspecies.goat_sequencing_status == 'sample_collected')):
                                    #messages.info(self.request, gss)
                                    targetspecies.goat_sequencing_status = gss or None
                        targetspecies.save()
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

                        if 'tags' in row:
                            for t in row['tags'].split(' '):
                                species_tag, created = Tag.objects.get_or_create(
                                    tag=t
                                )
                                targetspecies.tags.add(species_tag)

                        genometeam_record, created = GenomeTeam.objects.get_or_create(
                                    species=targetspecies
                                )
                        collection_record, created = SampleCollection.objects.get_or_create(
                                    species=targetspecies
                                )
                        sequencing_record, created = Sequencing.objects.get_or_create(
                                    species=targetspecies
                                )
                        assemblyproject_record, created = AssemblyProject.objects.get_or_create(
                                    species=targetspecies
                                )
                        annotation_record, created = Annotation.objects.get_or_create(
                                    species=targetspecies
                                )
                        cannotation_record, created = CommunityAnnotation.objects.get_or_create(
                                    species=targetspecies
                                )
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

                        collection_record.save()
                        
            
        messages.success(self.request, 'Species in list added successfully. Add more?')  
        #return HttpResponseRedirect(self.request.path_info)
        return super(NewSpeciesListView, self).form_valid(form)
 
#@login_required
def recipe_detail(request, pk=None):
    recipe = Recipe.objects.get(pk=pk)
    context = {"recipe": recipe,
               'build_page_title':'ERGA-GTC Recipe'
               }
    response = render(request, "recipe_detail.html", context)
    return response

#@login_required
def sample_detail(request, pk=None):
    sample = Sample.objects.get(pk=pk)
    site_url = settings.DEFAULT_DOMAIN
    context = {"sample": sample,
               "site_url": site_url,
               'build_page_title':'ERGA-GTC Sample'
               }
    response = render(request, "sample_detail.html", context)
    return response
