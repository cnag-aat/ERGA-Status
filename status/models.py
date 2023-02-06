from django.db import models
import os
import django.utils
from django.conf import settings
from multiselectfield import MultiSelectField
from django.core.mail import send_mail

def default_domain(request):
    return {'default_domain': settings.DEFAULT_DOMAIN}

# Create your models here.
STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Received', 'Received'),
    ('Processing', 'Processing'),
    ('Done', 'Done'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
)

COLLECTION_STATUS_CHOICES = (
    ('Long_Listed', 'Long_Listed'),
    ('Collecting', 'Collecting'),
    ('Resampling', 'Resampling'),
    ('COPO', 'COPO'),
    ('Submitted', 'Submitted'),
    ('Issue', 'Issue')
)

SEQUENCING_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Received', 'Received'),
    ('Extracted', 'Extracted'),
    ('Sequencing', 'Sequencing'),
    ('TopUp', 'TopUp'),
    ('External', 'External'),
    ('Submitted', 'Submitted'),
    ('Done', 'Done'),
    ('Issue', 'Issue')
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

CURATION_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Curating', 'Curating'),
    ('Done', 'Done'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
)

ANNOTATION_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Annotating', 'Annotating'),
    ('Done', 'Done'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
)

SUBMISSION_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Submitted', 'Submitted'),
    ('Issue', 'Issue')
)

SUBMISSION_DATATYPE_CHOICES = (
    ('DNA', 'DNA'),
    ('RNA', 'RNA'),
    ('Assembly', 'Assembly'),
    ('Annotation', 'Annotation')
)

ASSEMBLY_TYPE_CHOICES = (
    ('Primary', 'Pseudohaploid Primary'),
    ('Alternate', 'Pseudohaploid Alternate'),
    ('Hap1', 'Phased Haplotype 1'),
    ('Hap2', 'Phased Haplotype 2'),
    ('Maternal', 'Trio-phased Maternal'),
    ('Paternal', 'Trio-phased Paternal'),
    ('MT', 'Mitogenome'),
    ('Chloroplast', 'Chloroplast'),
    ('Endosymbiont', 'Endosymbiont')
)

ROLE_CHOICES = (
    ('sample_handling_team', 'Sample Handling Team'),
    ('sample_coordinator', 'Sample Coordinator'),
    ('collection_team', 'Collection Team'),
    ('taxonomy_team', 'Taxonomy Team'),
    ('vouchering_team', 'Vouchering Team'),
    ('barcoding_team', 'Barcoding Team'),
    ('sequencing_team', 'Sequencing Team'),
    ('assembly_team', 'Assembly Team'),
    ('community_annotation_team_', 'Community Annotation Team'),
    ('annotation_team', 'Annotation Team'),
    ('other', 'Other'),
)

class Role(models.Model):
    description = models.CharField(max_length=100, choices=ROLE_CHOICES, default='other')
    class Meta:
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.description


class TaxonKingdom(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'kingdoms'

    def __str__(self):
        return self.name

class TaxonPhylum(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'phyla'

    def __str__(self):
        return self.name

class TaxonClass(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'classes'

    def __str__(self):
        return self.name

class TaxonOrder(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'orders'

    def __str__(self):
        return self.name

class TaxonFamily(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'families'

    def __str__(self):
        return self.name

class TaxonGenus(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_family = models.ForeignKey(TaxonFamily, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'genera'

    def __str__(self):
        return self.name

# class TaxonSpecies(models.Model):
#     taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     taxon_family = models.ForeignKey(TaxonFamily, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     taxon_genus = models.ForeignKey(TaxonGenus, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
#     name = models.CharField(max_length=100)
#     class Meta:
#         verbose_name_plural = 'species'
#
#     def __str__(self):
#         return self.name

class TargetSpecies(models.Model):
    scientific_name = models.CharField(max_length=201, blank=True, null=True, db_index=True)
    tolid_prefix = models.CharField(max_length=12, blank=True, null=True, db_index=True)
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Phylum")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Class")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Order")
    taxon_family = models.ForeignKey(TaxonFamily, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Family")
    taxon_genus = models.ForeignKey(TaxonGenus, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="Genus")
    # taxon_species = models.ForeignKey(TaxonSpecies, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Species")
    chromosome_number = models.IntegerField(null=True, blank=True)
    haploid_number = models.IntegerField(null=True, blank=True)
    ploidy = models.IntegerField(null=True, blank=True)
    taxon_id = models.CharField(max_length=20,unique=True, null=True, blank=True, db_index=True)
    c_value = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, verbose_name="C-value")
    genome_size = models.BigIntegerField(null=True, blank=True)

    class Meta:
        verbose_name_plural = 'species'
        ordering = ['taxon_kingdom', 'taxon_phylum', 'taxon_class', 'taxon_order','taxon_family','taxon_genus','scientific_name']

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('species_detail', args=[str(self.scientific_name)])

    def __str__(self):
        return self.scientific_name
        #return self.scientific_name +" (" + self.tolid_prefix + ")"

class CommonNames(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="Genus/species")
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'common names'

    def __str__(self):
        return self.name

class Synonyms(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="Genus/species")
    name = models.CharField(max_length=201, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'synonyms'

    def __str__(self):
        return self.name

class Affiliation(models.Model):
    affiliation = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'affiliations'

    def __str__(self):
        return self.affiliation

class UserProfile(models.Model):
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.CASCADE,
            related_name='user_profile'
        )
    first_name = models.CharField(max_length=60, verbose_name="First name")
    middle_name = models.CharField(null=True, blank=True, max_length=60, verbose_name="Middle name")
    last_name = models.CharField(max_length=60, verbose_name="Last name")
    roles = models.ManyToManyField(Role,default='other')
    lead = models.BooleanField(default=False)
    affiliation = models.ManyToManyField(Affiliation)
    orcid = models.CharField(null=True, blank=True, max_length=60, verbose_name="ORCID")
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('user_profile', args=[str(self.pk)])

    def __str__(self):
        return self.first_name + " " + self.last_name


class Person(models.Model):
    first_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.ManyToManyField(Affiliation)
    orcid = models.CharField(max_length=40, null=True, blank=True)
    email = models.EmailField(max_length=40, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'people'

    def __str__(self):
        return self.first_name + " " + self.last_name 

class AnnotationTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='annotation_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'annotation teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('annotation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class CommunityAnnotationTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='community_annotation_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'Community annotation teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('community_annotation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class BiobankingTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        #UserProfile,
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='biobanking_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'biobanking teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('biobanking_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class AssemblyTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='assembly_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'assembly teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class CurationTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='curation_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'curation teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('curation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class SequencingTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='sequencing_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'sequencing teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sequencing_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class ExtractionTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='extraction_team_lead'
    )

    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'extraction teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('extraction_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class CollectionTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='collection_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('collection_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class TaxonomyTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='taxonomy_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('taxonomy_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class SampleHandlingTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE, 
        related_name='sample_handling_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sample_handling_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class VoucheringTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.SET_NULL, null=True,
        related_name='vouchering_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('vouchering_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class BarcodingTeam(models.Model):
    name = models.CharField(max_length=100)
    lead = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='barcoding_team_lead'
    )
    members = models.ManyToManyField(UserProfile)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('barcoding_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.first_name +" (" + self.name + ")"

class Author(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name="author")
    role = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.author.first_name + " " + self.author.last_name

class GenomeTeam(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    sample_handling_team = models.ForeignKey(SampleHandlingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sample handling team")
    sample_coordinator = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sample_coordinator")
    collection_team = models.ForeignKey(CollectionTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="collection team")
    taxonomy_team = models.ForeignKey(TaxonomyTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="taxonomy team")
    vouchering_team = models.ForeignKey(VoucheringTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="vouchering team")
    barcoding_team = models.ForeignKey(BarcodingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="barcoding team")
    biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
    extraction_team = models.ForeignKey(ExtractionTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="nucleic acid extraction team")
    sequencing_team = models.ForeignKey(SequencingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sequencing team")
    assembly_team = models.ForeignKey(AssemblyTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="assembly team")
    community_annotation_team = models.ForeignKey(CommunityAnnotationTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="community annotation team")
    annotation_team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="annotation team")

    class Meta:
        verbose_name_plural = 'genome teams'
    
    def __str__(self):
        return self.species.scientific_name




class SampleCollection(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",unique=True)
    team = models.ForeignKey(CollectionTeam, on_delete=models.SET_NULL, null=True, verbose_name="collection team", blank=True)
    genomic_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    rna_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    #hic_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'collection'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('collection_list', args=[self.species])

    def __str__(self):
        return self.species.scientific_name 

class Specimen(models.Model):
    # TISSUE_REMOVED_FOR_BIOBANKING	TISSUE_VOUCHER_ID_FOR_BIOBANKING	TISSUE_FOR_BIOBANKING	
    # DNA_REMOVED_FOR_BIOBANKING	DNA_VOUCHER_ID_FOR_BIOBANKING	
    # VOUCHER_ID	 PROXY_VOUCHER_ID	VOUCHER_LINK	PROXY_VOUCHER_LINK	VOUCHER_INSTITUTION
    specimen_id = models.CharField(max_length=20, help_text='Internal Specimen ID')
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    barcode = models.CharField(max_length=20, help_text='Tube barcode')
    tolid = models.CharField(max_length=20, help_text='Registered ToLID for the Specimen', null=True, blank=True)
    collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
    sample_coordinator = models.CharField(max_length=50, help_text='Sample coordinator', null=True, blank=True)
    tissue_removed_for_biobanking = models.BooleanField(default=False)
    tissue_voucher_id_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    tissue_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    dna_removed_for_biobanking = models.BooleanField(default=False)
    dna_voucher_id_for_biobanking = models.CharField(max_length=50, null=True, blank=True)
    voucher_id = models.CharField(max_length=50, help_text='Voucher ID', null=True, blank=True)
    proxy_voucher_id = models.CharField(max_length=50, help_text='Proxy voucher ID', null=True, blank=True)
    voucher_link = models.CharField(max_length=200, null=True, blank=True)
    proxy_voucher_link = models.CharField(max_length=200, null=True, blank=True)
    voucher_institution = models.CharField(max_length=200, null=True, blank=True)
    
class Sample(models.Model):
    copo_id = models.CharField(max_length=30, help_text='COPO ID', null=True, blank=True, verbose_name="CopoID")
    biosampleAccession = models.CharField(max_length=20, help_text='BioSample Accession', null=True, blank=True, verbose_name="BioSample")
    barcode = models.CharField(max_length=20, help_text='Tube barcode', null=True, blank=True)
    # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
    purpose_of_specimen = models.CharField(max_length=30, help_text='Purpose', null=True, blank=True)
    gal = models.CharField(max_length=120, help_text='GAL', null=True, blank=True, verbose_name="GAL")
    collector_sample_id = models.CharField(max_length=40, help_text='Collector Sample ID', null=True, blank=True)
    copo_date = models.CharField(max_length=30, help_text='COPO Time Updated', null=True, blank=True, verbose_name="date")
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, verbose_name="Specimen")

class Sequencing(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(SequencingTeam, on_delete=models.SET_NULL, null=True, verbose_name="sequencing team")
    genomic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    hic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    rna_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    ont_target = models.BigIntegerField(null=True, blank=True, verbose_name="ONT target")
    hifi_target = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi target")
    hic_target = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C target")
    short_target = models.BigIntegerField(null=True, blank=True, verbose_name="Short read target")
    rnaseq_numlibs_target = models.IntegerField(null=True, blank=True, verbose_name="RNAseq libs target")
    
    __original_genomic_seq_status = None
    __original_hic_seq_status = None
    __original_rna_seq_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_genomic_seq_status = self.genomic_seq_status
        self.__original_hic_seq_status = self.hic_seq_status
        self.__original_rna_seq_status = self.rna_seq_status

    def save(self, *args, **kwargs):
        if settings.NOTIFICATIONS == True:

            if ((self.__original_genomic_seq_status != 'Done' and self.__original_genomic_seq_status != 'Submitted') and (self.genomic_seq_status == 'Done' or self.genomic_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam = GenomeTeam.objects.get(species=self.species)
                assembly_team = AssemblyTeam.objects.get(genometeam=gteam)
                send_mail(
                    '[ERGA] Genomic sequencing for '+ self.species.scientific_name +'is done',
                    'Dear '+ assembly_team.lead.first_name+",\n\nGenomic sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                    'denovo@cnag.crg.eu',
                    [assembly_team.lead.email],
                    fail_silently=True,
                )

            if ((self.__original_hic_seq_status != 'Done' and self.__original_hic_seq_status != 'Submitted') and (self.hic_seq_status == 'Done' or self.hic_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam = GenomeTeam.objects.get(species=self.species)
                assembly_team = AssemblyTeam.objects.get(genometeam=gteam)
                send_mail(
                    '[ERGA] Hi-C sequencing for '+ self.species.scientific_name +'is done',
                    'Dear '+ assembly_team.lead.first_name+",\n\nHi-C sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                    'denovo@cnag.crg.eu',
                    [assembly_team.lead.email],
                    fail_silently=True,
                )

            if ((self.__original_rna_seq_status != 'Done' and self.__original_rna_seq_status != 'Submitted') and (self.rna_seq_status == 'Done' or self.rna_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam = GenomeTeam.objects.get(species=self.species)
                if CommunityAnnotationTeam.objects.filter(genometeam=gteam).exists():
                    community_annotation_team = CommunityAnnotationTeam.objects.get(genometeam=gteam)
                    send_mail(
                        '[ERGA] RNA sequencing for '+ self.species.scientific_name +'is done',
                        'Dear '+ community_annotation_team.lead.first_name+",\n\nRNA sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                        'denovo@cnag.crg.eu',
                        [community_annotation_team.lead.email],
                        fail_silently=True,
                    )

        if self.__original_genomic_seq_status == 'Waiting' and self.genomic_seq_status != 'Waiting':
            gteam = GenomeTeam.objects.get(species=self.species)
            team = SequencingTeam.objects.get(genometeam=gteam)
            for m in team.members.all():
                species_authors, created = Author.objects.get_or_create(
                    species=self.species,
                    author=m,
                    role='sequencing'
                )
        super(Sequencing, self).save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        #return reverse('sequencing_list',kwargs=)
        return reverse('sequencing_list', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'sequencing'

    def __str__(self):
        return self.species.scientific_name

class Reads(models.Model):
    project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    ont_yield = models.BigIntegerField(null=True, blank=True, verbose_name="ONT yield")
    hifi_yield = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi yield")
    hic_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C yield")
    short_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Short read yield")
    rnaseq_numlibs = models.IntegerField(null=True, blank=True, verbose_name="RNAseq libs")
    ont_ena = models.CharField(max_length=12, null=True, blank=True, verbose_name="ONT Accession")
    hifi_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="HiFi Accession")
    hic_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Hi-C Accession")
    short_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Short read Accession")
    rnaseq_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="RNAseq Accession")

    class Meta:
        verbose_name_plural = 'reads'

    def __str__(self):
        return self.project.species.scientific_name

class Curation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(CurationTeam, on_delete=models.SET_NULL, null=True, verbose_name="curation team")
    status = models.CharField(max_length=12, help_text='Status', choices=CURATION_STATUS_CHOICES, default=CURATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'curation'

    def __str__(self):
        return self.species.tolid_prefix

class CommunityAnnotation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, verbose_name="annotation team")
    status = models.CharField(max_length=12, help_text='Status', choices=ANNOTATION_STATUS_CHOICES, default=ANNOTATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status != 'Waiting':
            gteam = GenomeTeam.objects.get(species=self.species)
            team = CommunityAnnotationTeam.objects.get(genometeam=gteam)
            for m in team.members.all():
                species_authors, created = Author.objects.get_or_create(
                    species=self.species,
                    author=m,
                    role='community annotation'
                )
        super(CommunityAnnotation, self).save(*args, **kwargs)

class Annotation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, verbose_name="annotation team")
    status = models.CharField(max_length=12, help_text='Status', choices=ANNOTATION_STATUS_CHOICES, default=ANNOTATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.status != 'Waiting':
            gteam = GenomeTeam.objects.get(species=self.species)
            team = AnnotationTeam.objects.get(genometeam=gteam)
            for m in team.members.all():
                species_authors, created = Author.objects.get_or_create(
                    species=self.species,
                    author=m,
                    role='annotation'
                )
        super(annotation, self).save(*args, **kwargs)
 
    class Meta:
        verbose_name_plural = 'annotation'

    def __str__(self):
        return self.species.scientific_name

""" class Submission(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(SubmissionTeam, on_delete=models.SET_NULL, null=True, verbose_name="submission team")
    status = models.CharField(max_length=12, help_text='Status', choices=SUBMISSION_STATUS_CHOICES, default='Waiting')
    datatype = models.CharField(max_length=12, help_text='Data Type', choices=SUBMISSION_DATATYPE_CHOICES, default=SUBMISSION_DATATYPE_CHOICES[0][0])
    accession = models.CharField(max_length=20, help_text='ENA Accession Number', null=True, blank=True)
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'submission'

    def __str__(self):
        return self.species.scientific_name """

class AssemblyProject(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(AssemblyTeam, on_delete=models.SET_NULL, null=True, verbose_name="assembly team")
    status = models.CharField(max_length=12, help_text='Status', choices=ASSEMBLY_STATUS_CHOICES, default=ASSEMBLY_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'assembly projects'

    def save(self, *args, **kwargs):
        if self.status != 'Waiting':
            gteam = GenomeTeam.objects.get(species=self.species)
            team = AssemblyTeam.objects.get(genometeam=gteam)
            for m in team.members.all():
                species_authors, created = Author.objects.get_or_create(
                    species=self.species,
                    author=m,
                    role='assembly'
                )
        super(AssemblyProject, self).save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_project_list', args=[str(self.pk)])

    def __str__(self):
        return self.species.scientific_name

class AssemblyPipeline(models.Model):
    name = models.CharField(max_length=30, help_text='Pipeline name')
    version = models.CharField(max_length=10, help_text='Version')
    contigger = models.CharField(max_length=30, help_text='Main assembler')
    scaffolder = models.CharField(max_length=30, help_text='Scaffolder (can be the same as assembler)')
    url = models.CharField(max_length=300, help_text='URL', null=True, blank=True)
    description = models.TextField(max_length=2000, help_text='Full description of pipeline', null=True, blank=True)
    class Meta:
        verbose_name_plural = 'assembly pipelines'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_pipeline_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name + "." + self.version

class BUSCOdb(models.Model):
    db = models.CharField(max_length=60, db_index=True)
    class Meta:
        verbose_name_plural = 'BUSCO dbs'

    def __str__(self):
        return self.db

class BUSCOversion(models.Model):
    version = models.CharField(max_length=10, db_index=True)
    class Meta:
        verbose_name_plural = 'BUSCO versions'

    def __str__(self):
        return self.version

class Assembly(models.Model):
    project = models.ForeignKey(AssemblyProject, on_delete=models.CASCADE, verbose_name="Assembly project")
    description = models.CharField(null=True, blank=True, max_length=100)
    pipeline = models.ForeignKey(AssemblyPipeline, on_delete=models.SET_NULL, null=True, verbose_name="Assembly pipeline", blank=True )
    type = models.CharField(max_length=20, help_text='Type of assembly', choices=ASSEMBLY_TYPE_CHOICES, default='Primary')
    span = models.BigIntegerField(null=True, blank=True, verbose_name="Assembly span")
    contig_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Contig N50")
    scaffold_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Scaffold N50")
    chromosome_level =  models.NullBooleanField(blank=True, null=True, verbose_name="Chr level")
    percent_placed = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Pct. placed")
    busco = models.CharField(null=True, blank=True, max_length=60, verbose_name="BUSCO")
    busco_db = models.ForeignKey(BUSCOdb, on_delete=models.SET_NULL, null=True, verbose_name="BUSCO db", blank=True)
    busco_version = models.ForeignKey(BUSCOversion, on_delete=models.SET_NULL, null=True, verbose_name="BUSCO version", blank=True)
    qv = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="QV")

    class Meta:
        verbose_name_plural = 'assemblies'

    def __str__(self):
        return self.project.species.tolid_prefix + '.' + self.type

