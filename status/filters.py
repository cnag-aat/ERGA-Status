import django_filters
from django_filters  import FilterSet
from django_filters  import ChoiceFilter
from status.models import GenomeTeam
from status.models import TargetSpecies
from status.models import SequencingTeam
# from status.models import Tag
from django import forms
from django.db.models import Q

class GenomeTeamFilter(django_filters.FilterSet):
    # species__tags__tag = django_filters.ModelChoiceFilter(label='tags',queryset=Tag.objects.all())
    class Meta:
        model = GenomeTeam
        fields = [
            # 'species__tags__tag',
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

class TargetSpeciesFilter(django_filters.FilterSet):
    gt_rel__sequencing_team = django_filters.ModelChoiceFilter(label='Center',queryset=SequencingTeam.objects.all())
    SEQSTATUS_CHOICES = (
        ('Waiting', 'Waiting'),
    	('Received', 'Received'),
		('Prep', 'Prep'),
		('Extracted', 'Extracted'),
		('Sequencing', 'Sequencing'),
		('TopUp', 'TopUp'),
		('External', 'External'),
		('Submitted', 'Submitted'),
		('Done', 'Done'),
		('Issue', 'Issue'),
    )
    ASSEMBLY_STATUS_CHOICES = (
		('Waiting', 'Waiting'),
		('Assembling', 'Assembling'),
		('Contigs', 'Contigs'),
		('Scaffolding', 'Scaffolding'),
		('Scaffolds', 'Scaffolds'),
		('Curating', 'Curating'),
		('Done', 'Done'),
		('Submitted', 'Submitted'),
		('Issue', 'Issue')
	)
    ANNOTATION_STATUS_CHOICES = (
		('Waiting', 'Waiting'),
		('Annotating', 'Annotating'),
		('Done', 'Done'),
		('Sent', 'Sent'),
		('Issue', 'Issue')
	)
    long_seq_status = django_filters.ChoiceFilter(field_name='sequencing_rel__long_seq_status',label='Long Read Status',choices=SEQSTATUS_CHOICES,null_label=None)

    #long_seq_status = django_filters.CharFilter(field_name='sequencing__long_seq_status',label='Long Read Status')
    short_seq_status = django_filters.ChoiceFilter(field_name='sequencing_rel__short_seq_status',label='Short Read Status',choices=SEQSTATUS_CHOICES,null_label=None)
    hic_seq_status = django_filters.ChoiceFilter(field_name='sequencing_rel__hic_seq_status',label='Hi-C Status',choices=SEQSTATUS_CHOICES,null_label=None)
    rna_seq_status = django_filters.ChoiceFilter(field_name='sequencing_rel__rna_seq_status',label='RNA-Seq Status',choices=SEQSTATUS_CHOICES,null_label=None)
    assembly_status = django_filters.ChoiceFilter(field_name='assembly_rel__status',label='Assembly Status',choices=ASSEMBLY_STATUS_CHOICES,null_label=None)
    annotation_status = django_filters.ChoiceFilter(field_name='annotation__status',label='Annotation Status',choices=ANNOTATION_STATUS_CHOICES,null_label=None)
    community_annotation_status = django_filters.ChoiceFilter(field_name='communityannotation__status',label='Community Annotation Status',choices=ANNOTATION_STATUS_CHOICES,null_label=None)

    class Meta:
        model = TargetSpecies
        fields = [
            'scientific_name',
            'tolid_prefix',
        	'gt_rel__sequencing_team',
        	'goat_sequencing_status',
            # 'tags',
        	'sequencing_rel__long_seq_status',
        	'sequencing_rel__short_seq_status', 
        	'sequencing_rel__hic_seq_status', 
       		'sequencing_rel__rna_seq_status', 
    		'assembly_status',
        	'annotation_status',
        	'community_annotation_status',
            'taxon_kingdom',
            'taxon_phylum',
            'taxon_class',
            'taxon_order',
            'taxon_family',
            'taxon_genus'
            ]
