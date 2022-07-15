# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models import *
import re
from django.utils.safestring import mark_safe
#import html
class TargetSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        #attrs = {"class": "table-sm"}
        #fields = ('scaffold','start','end','orientation','roary_gene','gene','st')
        #fields = ("name", )
        #id = tables.Column(linkify=True)

class AssemblyTable(tables.Table):
    export_formats = ['csv', 'tsv']
    class Meta:
        model = Assembly
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}

class AssemblyProjectTable(tables.Table):
    export_formats = ['csv', 'tsv']
    assemblies = tables.TemplateColumn('<a href="{% url \'assembly\' %}?project={{record.pk}}>assemblies</a>',empty_values=(), verbose_name='Assemblies')

    class Meta:
        model = AssemblyProject
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team','assemblies', 'status')
