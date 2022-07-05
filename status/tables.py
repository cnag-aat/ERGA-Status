# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models import TargetSpecies
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
