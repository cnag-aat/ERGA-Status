import django_filters
from django_filters  import FilterSet
from django_filters  import ChoiceFilter
from django_filters  import RangeFilter
from django_filters  import CharFilter
from status.models import Reads
from status.models import GenomeTeam
from status.models import TargetSpecies
from status.models import SequencingTeam
from status.models import AssemblyTeam
from status.models import Task
from status.models import Assembly
from status.models import Specimen
from status.models import Sample
from status.models import SampleCollection
# from status.models import Tag
from django import forms
from django.db.models import Q

COPO_STATUS_CHOICES = (
	('Not submitted', 'Not submitted'),
	('Rejected', 'Rejected'),
	('Accepted', 'Accepted'),
	('Pending', 'Pending')
)
class GenomeTeamFilter(django_filters.FilterSet):
    # species__tags__tag = django_filters.ModelChoiceFilter(label='tags',queryset=Tag.objects.all())	
	species = django_filters.CharFilter(field_name='species',lookup_expr='icontains',label='Species')
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

class OverviewSpeciesFilter(django_filters.FilterSet):
    collection_rel__task = django_filters.ModelChoiceFilter(label='Task',queryset=Task.objects.all())
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
		('UnderReview', 'UnderReview'),
		('Approved', 'Approved'),
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
    COPO_STATUS_CHOICES = (
		('Not submitted', 'Not submitted'),
		('Rejected', 'Rejected'),
		('Accepted', 'Accepted'),
		('Pending', 'Pending')
	)
    copo_status = django_filters.ChoiceFilter(field_name='collection_rel__copo_status',label='COPO Status',choices=COPO_STATUS_CHOICES,null_label=None)
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
            'collection_rel__task',
            'copo_status',
        	'gt_rel__sequencing_team',
        	'goat_sequencing_status',
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
	listed_species = django_filters.CharFilter(field_name='listed_species',lookup_expr='icontains',label='Listed Species')
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

class ReadsFilter(django_filters.FilterSet):
	project__species__gt_rel__sequencing_team = django_filters.ModelChoiceFilter(label='Center',queryset=SequencingTeam.objects.all())
	class Meta:
		model = Reads
		fields = ['project__species__gt_rel__sequencing_team',]

class AssemblyFilter(django_filters.FilterSet):
	project__species__gt_rel__assembly_team = django_filters.ModelChoiceFilter(label='Assembly Team',queryset=AssemblyTeam.objects.all())
	class Meta:
		model = Assembly
		fields = ['project__species__gt_rel__assembly_team','pipeline','type','chromosome_level','accession','gca']

class SpecimenFilter(django_filters.FilterSet):
	q = django_filters.CharFilter(method='my_custom_filter', label="Search")
	species__gt_rel__sequencing_team = django_filters.ModelChoiceFilter(label='Center',queryset=SequencingTeam.objects.all())
	class Meta:
		model = Specimen
		exclude = ['GAL']
		fields = [
			'q',
			'species__gt_rel__sequencing_team',
			'species',
			'tolid',
			'specimen_id',
			'biosampleAccession',
			'sample_coordinator',
			'tissue_removed_for_biobanking',
			'tissue_voucher_id_for_biobanking',
			'proxy_tissue_voucher_id_for_biobanking',
			'tissue_for_biobanking',
			'dna_removed_for_biobanking',
			'dna_voucher_id_for_biobanking',
			'voucher_id',
			'proxy_voucher_id',
			'voucher_institution',
			'biobanking_team',
			]
	def my_custom_filter(self, queryset, name, value):
		return queryset.filter(
            Q(species__scientific_name__icontains=value) |
            Q(tolid=value) |
            Q(specimen_id__icontains=value) | 
            Q(biosampleAccession__icontains=value) | 
            Q(sample_coordinator__icontains=value) | 
            Q(tissue_voucher_id_for_biobanking__icontains=value) | 
            Q(proxy_tissue_voucher_id_for_biobanking__icontains=value)| 
            Q(dna_voucher_id_for_biobanking=value)| 
            Q(voucher_id=value)| 
            Q(proxy_voucher_id=value)| 
            Q(voucher_institution=value)
        )
class SampleFilter(django_filters.FilterSet):
	q = django_filters.CharFilter(method='my_custom_filter', label="Search")
	species__gt_rel__sequencing_team = django_filters.ModelChoiceFilter(label='Center',queryset=SequencingTeam.objects.all())
	copo_status = django_filters.ChoiceFilter(field_name='copo_status',label='COPO Status',choices=COPO_STATUS_CHOICES,null_label=None)
	class Meta:
		model = Sample
		fields = ['q',
			'species__gt_rel__sequencing_team',
			'species',
			'specimen',
			'copo_id',
			'biosampleAccession',
			'sampleDerivedFrom',
			'sampleSameAs',
			'tube_or_well_id',
			'gal_sample_id',
			'collector_sample_id',
			'corrected_id',
			'purpose_of_specimen',
			'copo_status',
			'leftover',
			'leftover_biobanking_team',
			]
	def my_custom_filter(self, queryset, name, value):
		return queryset.filter(
            Q(species__scientific_name__icontains=value) |
            Q(tube_or_well_id__icontains=value) | 
            Q(gal_sample_id__icontains=value) | 
            Q(collector_sample_id__icontains=value) | 
            Q(corrected_id__icontains=value) | 
            Q(specimen__specimen_id__icontains=value)| 
            Q(biosampleAccession=value)
        )
    # copo_id = models.CharField(max_length=30, help_text='COPO ID', null=True, blank=True, verbose_name="CopoID") # should make this unique and not nullable
    # biosampleAccession = models.CharField(max_length=20, help_text='BioSample Accession', null=True, blank=True, verbose_name="BioSample")
    # sampleDerivedFrom = models.CharField(max_length=20, help_text='BioSample Derived From', null=True, blank=True, verbose_name="SampleDerivedFrom")
    # sampleSameAs = models.CharField(max_length=20, help_text='BioSample Same As', null=True, blank=True, verbose_name="SampleSameAs")
    # barcode = models.CharField(max_length=50, help_text='Tube barcode', null=True, blank=True)
    # # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
    # purpose_of_specimen = models.CharField(max_length=30, help_text='Purpose', null=True, blank=True)
    # gal = models.CharField(max_length=120, help_text='GAL', null=True, blank=True, verbose_name="GAL")
    # gal_sample_id = models.CharField(max_length=200, help_text='GAL Sample ID', null=True, blank=True)
    # collector_sample_id = models.CharField(max_length=200, help_text='Collector Sample ID', null=True, blank=True)
    # tube_or_well_id = models.CharField(max_length=200, help_text='Tube or Well ID', null=True, blank=True)
    # corrected_id = models.CharField(max_length=200, help_text='Corrected ID', null=True, blank=True)
    # copo_date = models.CharField(max_length=50, help_text='COPO Time Updated', null=True, blank=True, verbose_name="date")
    # #copo_update_date = models.CharField(max_length=30, help_text='COPO Time Updated', null=True, blank=True, verbose_name="date")
    # copo_status = models.CharField(max_length=30, help_text='COPO Status', null=True, blank=True, verbose_name="Status")
    # specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, verbose_name="Specimen",null=True, blank=True)
    # species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",null=True, blank=True)
    # leftover = models.CharField(max_length=20, help_text='Leftover sample', choices=LEFTOVER_CHOICES, default=LEFTOVER_CHOICES[0][0])
    # leftover_biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
    # date_sent = models.DateField(blank=True,null=True)
    # date_received = models.DateField(blank=True,null=True)


class SampleCollectionFilter(django_filters.FilterSet):
	species_search = django_filters.CharFilter(field_name='species__scientific_name',lookup_expr='icontains',label='Species Search')
	sample_provider_name = django_filters.CharFilter(field_name='sample_provider_name',lookup_expr='icontains',label='Sample Provider')
	class Meta:
		model = SampleCollection
		fields = [
			'species_search',
			'species',
			'copo_status',
			'subproject',
			'task',
			'country',
			'sample_provider_name',
			'mta1',
			'mta2',
			'barcoding_status',
			'barcoding_results',
			'sampling_delay'
		]
	# species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",related_name='collection_rel')
    # copo_status = models.CharField(max_length=20, help_text='COPO status', choices=COPO_STATUS_CHOICES, default=COPO_STATUS_CHOICES[0][0])
    # note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    # subproject = models.ManyToManyField(Subproject,default=[0],blank=True,null=True)#default=1
    # task = models.ForeignKey(Task, on_delete=models.SET_NULL, verbose_name="Task", null=True, blank=True)
    # country = models.ForeignKey(Country, on_delete=models.SET_NULL, verbose_name="Country", null=True, blank=True)
    # sample_provider_name = models.CharField(max_length=100, null=True, blank=True)
    # sample_provider_email = models.CharField(max_length=150, null=True, blank=True)
    # mta1 =  models.BooleanField(default=False, verbose_name="MTA 1: Seq Centers")
    # mta2 =  models.BooleanField(default=False, verbose_name="MTA 2: LIB leftovers")
    # barcoding_status = models.CharField(max_length=30, help_text='Barcoding Status', choices=BARCODING_STATUS_CHOICES, default=BARCODING_STATUS_CHOICES[0][0])
    # barcoding_results = models.CharField(max_length=200, null=True, blank=True)
    # sampling_month = MonthDateField(blank=True,null=True)
    # deadline_manifest_sharing = models.DateField(blank=True,null=True)
    # deadline_manifest_acceptance = models.DateField(blank=True,null=True)
    # deadline_sample_shipment = models.DateField(blank=True,null=True)
    # sampling_delay = models.BooleanField(default=False, verbose_name="Delayed sample")
		# class Meta:
	# 	model = SampleCollection
	# 	fields = ['q',
	# 		'species__gt_rel__sequencing_team',
	# 		'species',
	# 		'specimen',
	# 		'copo_id',
	# 		'biosampleAccession',
	# 		'sampleDerivedFrom',
	# 		'sampleSameAs',
	# 		'tube_or_well_id',
	# 		'gal_sample_id',
	# 		'collector_sample_id',
	# 		'corrected_id',
	# 		'purpose_of_specimen',
	# 		'copo_status',
	# 		'leftover',
	# 		'leftover_biobanking_team',
	# 		]
	# def my_custom_filter(self, queryset, name, value):
	# 	return queryset.filter(
    #         Q(species__scientific_name__icontains=value) |
    #         Q(tube_or_well_id__icontains=value) | 
    #         Q(gal_sample_id__icontains=value) | 
    #         Q(collector_sample_id__icontains=value) | 
    #         Q(corrected_id__icontains=value) | 
    #         Q(specimen__specimen_id__icontains=value)| 
    #         Q(biosampleAccession=value)
    #     )

