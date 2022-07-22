from django.db import models
import os
from django.conf import settings


# Create your models here.
STATUS_CHOICES = (
    ('Waiting', 'Waiting for input'),
    ('Received', 'Input received'),
    ('Processing', 'Processing'),
    ('Done', 'Done'),
    ('Sent', 'Sent'),
    ('Issue', 'Issue')
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

class SampleCoordinator(models.Model):
    name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'sample coordinators'

    def __str__(self):
        return self.name

class AssemblyTeam(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    affiliation = models.CharField(max_length=100)
    # email = models.CharField(max_length=100)
    contact = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name_plural = 'assembly teams'

    # def get_absolute_url(self):
    #     from django.urls import reverse
    #     return reverse('assembly_team_detail', args=[str(self.contact)])

    def __str__(self):
        return self.contact.username + " ("+self.affiliation+")"

class CurationTeam(models.Model):
    name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'curation teams'

    def __str__(self):
        return self.name + " ("+self.affiliation+")"

class SequencingTeam(models.Model):
    name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'sequencing teams'

    def __str__(self):
        return self.name + " ("+self.affiliation+")"

class CollectionTeam(models.Model):
    name = models.CharField(max_length=100)
    affiliation = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'collection teams'

    def __str__(self):
        return self.name + " ("+self.affiliation+")"


class SampleCollection(models.Model):
    sample_coordinator = models.ForeignKey(SampleCoordinator, on_delete=models.CASCADE, verbose_name="sample coordinators")
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    status = models.CharField(max_length=12, help_text='Status', choices=STATUS_CHOICES, default='Waiting')

    class Meta:
        verbose_name_plural = 'collections'

    def __str__(self):
        return self.name

class AssemblyProject(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    team = models.ForeignKey(AssemblyTeam, on_delete=models.CASCADE, verbose_name="assembly team")
    status = models.CharField(max_length=12, help_text='Status', choices=STATUS_CHOICES, default='Waiting')
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'assembly projects'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('assembly_project_list', args=[str(self.species)])

    def __str__(self):
        return self.species.tolid_prefix + ' project'

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
    percent_placed = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="% placed")
    busco = models.CharField(null=True, blank=True, max_length=60, verbose_name="BUSCO")
    busco_db = models.ForeignKey(BUSCOdb, on_delete=models.CASCADE, verbose_name="BUSCO db", null=True, blank=True)
    busco_version = models.ForeignKey(BUSCOversion, on_delete=models.CASCADE, verbose_name="BUSCO version",null=True, blank=True)
    qv = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, verbose_name="QV")

    class Meta:
        verbose_name_plural = 'assemblies'

    def __str__(self):
        return self.project.species.tolid_prefix + '.' + self.type
