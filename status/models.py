from django.db import models
import os
from django.conf import settings


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
    ('Waiting', 'Waiting'),
    ('Sampling', 'Sampling'),
    ('Resampling', 'Resampling'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
)

SEQUENCING_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Sequencing', 'Sequencing'),
    ('TopUp', 'TopUp'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
)

ASSEMBLY_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Assembling', 'Assembling'),
    ('Done', 'Done'),
    ('Sent', 'Sent'),
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
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Phylum")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Class")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Order")
    taxon_family = models.ForeignKey(TaxonFamily, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Family")
    taxon_genus = models.ForeignKey(TaxonGenus, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Genus")
    # taxon_species = models.ForeignKey(TaxonSpecies, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Species")
    chromosome_number = models.IntegerField(null=True, blank=True)
    haploid_number = models.IntegerField(null=True, blank=True)
    ploidy = models.IntegerField(null=True, blank=True)
    taxon_id = models.IntegerField(unique=True, db_index=True)
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

class AnnotationTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='annotation_team_lead'
    )
    class Meta:
        verbose_name_plural = 'annotation teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('annotation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.username + " ("+self.affiliation+")"

class SubmissionTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submission_team_lead'
    )
    class Meta:
        verbose_name_plural = 'submission teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('submission_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.username + " ("+self.affiliation+")"

class AssemblyTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assembly_team_lead'
    )

    class Meta:
        verbose_name_plural = 'assembly teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.contact.username + " ("+self.affiliation+")"

class CurationTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='curation_team_lead'
    )
    class Meta:
        verbose_name_plural = 'curation teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('curation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.username + " ("+self.affiliation+")"

class SequencingTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    lead = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sequencing_team_lead'
    )
    reception = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sample_reception'
    )
    delivery = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='data_delivery'
    )
    class Meta:
        verbose_name_plural = 'sequencing teams'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sequencing_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.lead.username + " ("+self.affiliation+")"

class CollectionTeam(models.Model):
    affiliation = models.CharField(max_length=100)
    coordinator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='collection_team_lead'
    )

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('collection_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.coordinator.username + " ("+self.affiliation+")"


class SampleCollection(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(CollectionTeam, on_delete=models.CASCADE, verbose_name="collection team")
    genomic_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    rna_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    hic_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'collection'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('collection_list', args=[self.species])

    def __str__(self):
        return self.species.tolid_prefix

class Specimen(models.Model):
    specimen_id = models.CharField(max_length=20, help_text='Internal Specimen ID')
    barcode = models.CharField(max_length=20, help_text='Tube barcode')
    tolid = models.CharField(max_length=20, help_text='Registered ToLID for the Specimen', null=True, blank=True)
    collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")

class Sequencing(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(SequencingTeam, on_delete=models.CASCADE, verbose_name="sequencing team")
    genomic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    hic_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    rna_seq_status = models.CharField(max_length=12, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    ont_target = models.BigIntegerField(null=True, blank=True, verbose_name="ONT target")
    hifi_target = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi target")
    hic_target = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C target")
    short_target = models.BigIntegerField(null=True, blank=True, verbose_name="Short read target")
    rnaseq_numlibs_target = models.IntegerField(null=True, blank=True, verbose_name="RNAseq libs target")

    def get_absolute_url(self):
        from django.urls import reverse
        #return reverse('sequencing_list',kwargs=)
        return reverse('sequencing_list', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'sequencing'

    def __str__(self):
        return self.species.tolid_prefix

class Reads(models.Model):
    project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    ont_yield = models.BigIntegerField(null=True, blank=True, verbose_name="ONT yield")
    hifi_yield = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi yield")
    hic_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C yield")
    short_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Short read yield")
    rnaseq_numlibs = models.IntegerField(null=True, blank=True, verbose_name="RNAseq libs")

    class Meta:
        verbose_name_plural = 'reads'

    def __str__(self):
        return self.project.species.tolid_prefix

class Curation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(CurationTeam, on_delete=models.CASCADE, verbose_name="curation team")
    status = models.CharField(max_length=12, help_text='Status', choices=CURATION_STATUS_CHOICES, default=CURATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'curation'

    def __str__(self):
        return self.species.tolid_prefix

class Annotation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(AnnotationTeam, on_delete=models.CASCADE, verbose_name="annotation team")
    status = models.CharField(max_length=12, help_text='Status', choices=ANNOTATION_STATUS_CHOICES, default=ANNOTATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'annotation'

    def __str__(self):
        return self.species.tolid_prefix

class Submission(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(SubmissionTeam, on_delete=models.CASCADE, verbose_name="submission team")
    status = models.CharField(max_length=12, help_text='Status', choices=SUBMISSION_STATUS_CHOICES, default='Waiting')
    datatype = models.CharField(max_length=12, help_text='Data Type', choices=SUBMISSION_DATATYPE_CHOICES, default=SUBMISSION_DATATYPE_CHOICES[0][0])
    accession = models.CharField(max_length=20, help_text='ENA Accession Number', null=True, blank=True)
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'submission'

    def __str__(self):
        return self.species.tolid_prefix

class AssemblyProject(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(AssemblyTeam, on_delete=models.CASCADE, verbose_name="assembly team")
    status = models.CharField(max_length=12, help_text='Status', choices=ASSEMBLY_STATUS_CHOICES, default=ASSEMBLY_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'assembly projects'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_project_list', args=[str(self.species)])

    def __str__(self):
        return self.species.tolid_prefix

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
    type = models.CharField(max_length=20, help_text='Type of assembly', choices=ASSEMBLY_TYPE_CHOICES, default='Primary')
    span = models.BigIntegerField(null=True, blank=True, verbose_name="Assembly span")
    contig_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Contig N50")
    scaffold_n50 = models.BigIntegerField(null=True, blank=True, verbose_name="Scaffold N50")
    chromosome_level =  models.NullBooleanField(blank=True, null=True, verbose_name="Chr level")
    percent_placed = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="Pct. placed")
    busco = models.CharField(null=True, blank=True, max_length=60, verbose_name="BUSCO")
    busco_db = models.ForeignKey(BUSCOdb, on_delete=models.CASCADE, verbose_name="BUSCO db", null=True, blank=True)
    busco_version = models.ForeignKey(BUSCOversion, on_delete=models.CASCADE, verbose_name="BUSCO version",null=True, blank=True)
    qv = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="QV")

    class Meta:
        verbose_name_plural = 'assemblies'

    def __str__(self):
        return self.project.species.tolid_prefix + '.' + self.type
