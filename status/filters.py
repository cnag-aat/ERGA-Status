import django_filters
from django_filters  import FilterSet
from django_filters  import ChoiceFilter
from status.models import GenomeTeam
from status.models import Tag
from django import forms
from django.db.models import Q

class GenomeTeamFilter(django_filters.FilterSet):
    species__tags__tag = django_filters.ModelChoiceFilter(label='tags',queryset=Tag.objects.all())
    class Meta:
        model = GenomeTeam
        fields = [
            'species__tags__tag',
            'species',
        	'sample_handling_team',
        	'sample_coordinator',
        	'collection_team',
        	'taxonomy_team', 
        	'vouchering_team', 
       		'barcoding_team', 
    		'biobanking_team',
        	'sequencing_team',
        	'assembly_team', 
        	'community_annotation_team', 
        	'annotation_team' 
            ]