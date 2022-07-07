from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import ListView
from status.models import *
from django.views.generic import TemplateView
from django_tables2 import SingleTableView
from django_tables2 import RequestConfig

from status.tables import TargetSpeciesTable
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
    table_pagination = {"per_page": 15}
