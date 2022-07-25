# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models import *
import re
from django.utils.safestring import mark_safe
#import html
class OverviewTable(tables.Table):
    export_formats = ['csv', 'tsv']
    collection_status = tables.TemplateColumn('<span class="{{record.samplecollection.status}}">{{record.samplecollection.status}}</a>',empty_values=(), verbose_name='Collection')
    sequencing_status = tables.TemplateColumn('<span class="{{record.sequencing.status}}">{{record.sequencing.status}}</a>',empty_values=(), verbose_name='Sequencing')
    assembly_status = tables.TemplateColumn('<span class="{{record.assemblyproject.status}}">{{record.assemblyproject.status}}</a>',empty_values=(), verbose_name='Assembly')
    curation_status = tables.TemplateColumn('<span class="{{record.curation.status}}">{{record.curation.status}}</a>',empty_values=(), verbose_name='Curation')
    submission_status = tables.TemplateColumn('<span class="{{record.submission.status}}">{{record.submission.status}}</a>',empty_values=(), verbose_name='Submission')

    tolid_prefix = tables.Column(linkify=True)
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('tolid_prefix', 'scientific_name','collection_status','sequencing_status','assembly_status','curation_status','submission_status')

class TargetSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    scientific_name = tables.Column(linkify=True)
    tolid_prefix = tables.Column(linkify=True)
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('tolid_prefix', 'scientific_name','taxon_id', 'genome_size', 'c_value','ploidy','chromosome_number','haploid_number','taxon_kingdom','taxon_phylum','taxon_class','taxon','taxon_family','taxon_genus')

class AssemblyTable(tables.Table):
    export_formats = ['csv', 'tsv']
    project = tables.Column(linkify=True)
    class Meta:
        model = Assembly
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}

class AssemblyProjectTable(tables.Table):
    export_formats = ['csv', 'tsv']
    assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = AssemblyProject
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team','assemblies', 'note', 'status')
