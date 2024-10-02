import django_filters
from django_filters  import FilterSet
from django_filters  import ChoiceFilter
from django_filters  import RangeFilter
from django_filters  import CharFilter
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
    assembly_rank = django_filters.RangeFilter(field_name='assembly_rel__assembly_rank',label='Assembly level')
    scientific_name = django_filters.CharFilter(field_name='scientific_name',lookup_expr='icontains',label='Species')
    tolid_prefix = django_filters.CharFilter(field_name='tolid_prefix',lookup_expr='icontains',label='ToLID Prefix')

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

class SpeciesFilter(django_filters.FilterSet):
	GOAT_TARGET_LIST_STATUS_CHOICES = (
		('waiting_list', 'waiting_list'), #not shared with goat
		('none', 'none'),
		('long_list', 'long_list'),
		('other_priority', 'other_priority'),
		('family_representative', 'family_representative'),
		('removed', 'removed') #not shared with goat
	)
	GOAT_SEQUENCING_STATUS_CHOICES = (
		('none', 'none'),
		('in_collection','in_collection'), #not shared with goat
		('sample_collected', 'sample_collected'),
		('sample_acquired', 'sample_acquired'),
		('data_generation', 'data_generation'),
		('in_assembly', 'in_assembly'),
		('insdc_open', 'insdc_open'),
		('published', 'published')
	)
	listed_name = django_filters.CharFilter(field_name='listed_name',lookup_expr='icontains',label='Listed Species')
	scientific_name = django_filters.CharFilter(field_name='scientific_name',lookup_expr='icontains',label='Species')
	tolid_prefix = django_filters.CharFilter(field_name='tolid_prefix',lookup_expr='icontains',label='ToLID Prefix')
	goat_target_list_status = django_filters.ChoiceFilter(field_name='goat_target_list_status',label='GoaT Target Status',choices=GOAT_TARGET_LIST_STATUS_CHOICES,null_label=None)
	goat_sequencing_status = django_filters.ChoiceFilter(field_name='goat_sequencing_status',label='GoaT Sequencing Status',choices=GOAT_SEQUENCING_STATUS_CHOICES,null_label=None)
	class Meta:
		model = TargetSpecies
		exclude = ['gss_rank']
		# fields = [
        #     'listed_species',
        #     'scientific_name',
        #     'tolid_prefix',
        # 	'goat_target_list_status',
        # 	'goat_sequencing_status',
        #     # 'taxon_kingdom',
        #     # 'taxon_phylum',
        #     # 'taxon_class',
        #     # 'taxon_order',
        #     # 'taxon_family',
        #     # 'taxon_genus'
        #     ]