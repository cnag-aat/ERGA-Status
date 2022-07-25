# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models import *
import re
from django.utils.safestring import mark_safe
from django.utils.html import escape
#import html
class OverviewTable(tables.Table):
    export_formats = ['csv', 'tsv']
    collection_status = tables.LinkColumn("collection_list", kwargs={
                             species.pk: tables.A(species.pk)}, empty_values=(),accessor='samplecollection.status',verbose_name='Collection')
    sequencing_status = tables.Column(accessor='sequencing.status',verbose_name='Sequencing',linkify=True)
    assembly_status = tables.Column(accessor='assemblyproject.status',verbose_name='Assembly',linkify=True)
    curation_status = tables.Column(accessor='curation.status',verbose_name='Curation',linkify=True)
    annotation_status = tables.Column(accessor='annotation.status',verbose_name='Annotation',linkify=True)
    submission_status = tables.Column(accessor='submission.status',verbose_name='Submission',linkify=True)

    tolid_prefix = tables.Column(linkify=True)
    attrs={"td": {"class": "overview-table"}}

    # def render_collection_status(self, value):
    #     return mark_safe('<a href="'+
    #         url('collection_list',kwargs={'scientific_name': record.scientific_name})
    #         +'"><span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_collection_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_sequencing_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_assembly_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_curation_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_annotation_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_submission_status(self, value):
        return mark_safe('<span class="'+escape(value)+'">'+escape(value)+'</span>')

    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('tolid_prefix', 'scientific_name','collection_status','sequencing_status','assembly_status','curation_status','annotation_status','submission_status')

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

class SampleCollectionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = SampleCollection
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class SequencingTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Sequencing
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class CurationTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Curation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class AnnotationTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class SubmissionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Submission
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')
