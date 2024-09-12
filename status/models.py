from django.db import models
import os
import sys
import django.utils
from django.conf import settings
from multiselectfield import MultiSelectField
from django.core.mail import send_mail
from django.urls import reverse
import tagging
from tagging.fields import TagField
from django.dispatch import receiver
import subprocess
import csv
import time
from django.contrib import messages
#from tagging.registry import register


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
    ('Not collected', 'Not collected'),
    #('Long List', 'Long List'),
    ('Collecting', 'Collecting'),
    ('Collected', 'Collected'),
    ('Resampling', 'Resampling'),
    #('COPO', 'COPO'),
    ('Submitted', 'Submitted'),
    ('Pending', 'Pending'),
    ('Rejected', 'Rejected'),
    ('Issue', 'Issue')
)
COPO_STATUS_CHOICES = (
    ('Not submitted', 'Not submitted'),
    ('Rejected', 'Rejected'),
    ('Accepted', 'Accepted'),
    ('Pending', 'Pending')
)
SEQUENCING_STATUS_CHOICES = (
    ('Waiting', 'Waiting'),
    ('Received', 'Received'),
    ('Prep', 'Prep'),
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
    ('UnderReview', 'UnderReview'),
    ('Approved', 'Approved'),
    ('Submitted', 'Submitted'),
    ('Issue', 'Issue')
)
assembly_rank = {
    'Waiting':0,
    'Issue':1,
    'Assembling':2,
    'Contigs':3,
    'Scaffolding':4,
    'Scaffolds':5,
    'Curating':6,
    'Done':7,
    'UnderReview':8,
    'Approved':9,
    'Submitted':10
}

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
    ('Submitted', 'Submitted'),
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
    ('community_annotation_team', 'Community Annotation Team'),
    ('annotation_team', 'Annotation Team'),
    ('other', 'Other'),
)

READ_TYPES = (
    ('ONT', 'ONT'),
    ('HiFi', 'HiFi'),
    ('Illumina', 'Illumina'),
    ('HiC', 'HiC'),
    ('RNA', 'RNA')
)

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

gss_rank = {
    'none':0,
    'in_collection':1,
    'sample_collected':2,
    'sample_acquired':3,
    'data_generation':4,
    'in_assembly':5,
    'insdc_open':6,
    'published':7
}

class Role(models.Model):
    description = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'roles'

    def __str__(self):
        return self.description or str(self.id)

class Statement(models.Model):
    name = models.CharField(max_length=100)
    statement = models.TextField(max_length=2000)
    class Meta:
        verbose_name_plural = 'statements'

    def __str__(self):
        return self.statement or str(self.id)

# class Tag(models.Model):
#     tag = models.CharField(max_length=50, default='erga_long_list')
#     class Meta:
#         verbose_name_plural = 'tags'

#     def __str__(self):
#         return self.tag or str(self.id)
    
class TaxonKingdom(models.Model):
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'kingdoms'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TaxonPhylum(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'phyla'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TaxonClass(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'classes'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TaxonOrder(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'orders'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TaxonFamily(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'families'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TaxonGenus(models.Model):
    taxon_kingdom = models.ForeignKey(TaxonKingdom, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_phylum = models.ForeignKey(TaxonPhylum, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_class = models.ForeignKey(TaxonClass, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_order = models.ForeignKey(TaxonOrder, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    taxon_family = models.ForeignKey(TaxonFamily, blank=True, null=True, on_delete=models.CASCADE, verbose_name="Kingdom")
    name = models.CharField(max_length=100)
    class Meta:
        verbose_name_plural = 'genera'
        ordering = ("name",)

    def __str__(self):
        return self.name or str(self.id)

class TargetSpecies(models.Model):
    # ncbi_taxon_id	species	subspecies	family	target_list_status	sequencing_status	synonym	publication_id
    listed_species = models.CharField(max_length=201, blank=True, null=True)
    scientific_name = models.CharField(max_length=201, blank=True, null=True, db_index=True)
    #tags = models.ManyToManyField(Tag,default='erga_long_list',blank=True, null=True)
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
    subspecies = models.CharField(max_length=100, verbose_name="Subspecies", blank=True, null=True)
    goat_target_list_status = models.CharField(max_length=30, verbose_name="target_list_status", help_text='Target List Status', choices=GOAT_TARGET_LIST_STATUS_CHOICES, default=GOAT_TARGET_LIST_STATUS_CHOICES[0][0])
    goat_sequencing_status = models.CharField(max_length=30, blank=True, null=True, verbose_name="GoaT Sequencing Status", help_text='Sequencing Status', choices=GOAT_SEQUENCING_STATUS_CHOICES, default=GOAT_SEQUENCING_STATUS_CHOICES[0][0])
    gss_rank = models.IntegerField(null=True, blank=True, default=0)
    synonym = models.CharField(max_length=100, verbose_name="Synonym", blank=True, null=True)
    publication_id = models.CharField(max_length=50, verbose_name="Publication ID", blank=True, null=True)
    iucn_code = models.CharField(max_length=10, verbose_name="IUCN Assessment", blank=True, null=True)
    iucn_url = models.URLField(max_length = 400, null=True, blank=True, verbose_name="IUCN Page")
    date_updated = models.DateTimeField(auto_now=True)
    goat = models.BooleanField(default=False)  

    def save(self, *args, **kwargs):
        if not self.goat_target_list_status:
            self.goat_target_list_status = 'none'
        if not self.goat_sequencing_status:
            self.goat_sequencing_status = 'none'
        else:
            self.gss_rank = gss_rank[self.goat_sequencing_status]
        if self.taxon_id:
            found_in_goat=0
            print(self.listed_species)
            #process = subprocess.run('/home/www/resistome.cnag.cat/incredible/search/mash dist -i /home/www/resistome.cnag.cat/incredible/search/incredble.release7.fasta.msh /home/www/resistome.cnag.cat/incredible/deployment/data/'+ new_query.fasta.name +' | /home/www/resistome.cnag.cat/incredible/search/mash_hits_to_json.pl', shell=True, check=True, stdout=subprocess.PIPE, universal_newlines=True)
            #output = process.stdout
            #targetspecies = TargetSpecies.objects.get(taxon_id=self.taxon_id)
            tempfile = '/home/talioto/tmp/' + self.taxon_id + '.' + str(time.time()) + '.tsv'
            process = subprocess.run('/home/www/resistome.cnag.cat/erga-dev/scripts/query_goat.pl -taxid '+ self.taxon_id +" > "+ tempfile + ";chmod -R 777 "+tempfile+";", shell=True,  universal_newlines=True)      
            #process = subprocess.run('/home/www/resistome.cnag.cat/erga-dev/scripts/query_goat.pl -taxid '+ self.taxon_id +" > "+ tempfile + ";chmod -R 777 /home/talioto/tmp/;", shell=True,  universal_newlines=True)             process = subprocess.run('/home/www/resistome.cnag.cat/erga-dev/scripts/query_goat.pl -taxid '+ self.taxon_id +" > "+ tempfile + ";chmod -R 777 /home/talioto/tmp/;", shell=True,  universal_newlines=True)
           #encoding = 'ascii'
            #output = process.stdout
            with open(tempfile, 'r') as csvfile:
                csvreader = csv.DictReader(csvfile, delimiter='\t')
                #csvreader = csv.DictReader(output, delimiter='\t')
                #print("reading csv\n")
                for row in csvreader:  
                    print(row)
                    if row['scientific_name'] and row['scientific_name'].strip():
                        found_in_goat = True
                        self.goat = True
                        t_kingdom = None
                        if row['kingdom']:
                            t_kingdom, _ = TaxonKingdom.objects.get_or_create(
                                name=row['kingdom'],
                            )
                        t_phylum = None
                        if row['phylum']:
                            t_phylum, _ = TaxonPhylum.objects.get_or_create(
                                name=row['phylum'],
                                taxon_kingdom=t_kingdom
                            )
                        t_class = None
                        if row['class']:
                            t_class, _ = TaxonClass.objects.get_or_create(
                                name=row['class'],
                                taxon_kingdom=t_kingdom,
                                taxon_phylum=t_phylum,
                            )
                        t_order = None
                        if row['order']:
                            t_order, _ = TaxonOrder.objects.get_or_create(
                                name=row['order'],
                                taxon_kingdom=t_kingdom,
                                taxon_phylum=t_phylum,
                                taxon_class=t_class,
                            )
                        t_family = None
                        if row['family']:
                            t_family, _ = TaxonFamily.objects.get_or_create(
                                name=row['family'],
                                taxon_kingdom=t_kingdom,
                                taxon_phylum=t_phylum,
                                taxon_class=t_class,
                                taxon_order=t_order,
                            )
                        t_genus = None
                        if row['genus']:
                            t_genus, _ = TaxonGenus.objects.get_or_create(
                                name=row['genus'],
                                taxon_kingdom=t_kingdom,
                                taxon_phylum=t_phylum,
                                taxon_class=t_class,
                                taxon_order=t_order,
                                taxon_family=t_family,
                            )

                        #self.listed_species = row['original_species'] or None
                        self.scientific_name = row['scientific_name'] or None
                        #print (row['scientific_name'] + " " + self.scientific_name)
                        if self.tolid_prefix is None or len(self.tolid_prefix) == 0:
                            self.tolid_prefix = row['tolid_prefix'] or None
                        self.chromosome_number = row['chromosome_number'] or None
                        self.haploid_number = row['haploid_number'] or None
                        self.ploidy = row['ploidy'] or None
                        self.c_value = row['c_value'] or None
                        self.genome_size = round(float(row['genome_size'])) or None
                        self.taxon_kingdom = t_kingdom or None
                        self.taxon_phylum = t_phylum or None
                        self.taxon_class = t_class or None
                        self.taxon_order = t_order or None
                        if self.taxon_family is None:
                            self.taxon_family = t_family or None
                        self.taxon_genus = t_genus or None
                        #targetspecies.common_name = row['common_name'] or None
                        #self.synonym = row['synonym'] or None #do not update synonym from GoaT. this field is for providing a synonym TO GoaT if conflict with NCBI taxonomy
                        #self.goat_target_list_status = row['goat_target_list_status'] or None
                        #self.goat_sequencing_status = row['goat_sequencing_status'] or None
                        # if row['tags'] or None:
                        #     for t in row['tags'].split(' '):
                        #         species_tag, created = Tag.objects.get_or_create(
                        #             tag=t
                        #         )
                        #         self.tags.add(species_tag)
                        
                        if row['synonym'] or None:
                            for syn in row['synonym'].split(','):
                                species_synonyms, created = Synonyms.objects.get_or_create(
                                    name=syn,
                                    species=self
                                )

                        if row['common_name'] or None:
                            for cname in row['common_name'].split(','):
                                species_cnames, created = CommonNames.objects.get_or_create(
                                    name=cname,
                                    species=self
                                )
                    else:
                       self.taxon_id = "" 
            if not (found_in_goat):
                self.taxon_id = "" 
            os.remove(tempfile)

        super(TargetSpecies, self).save(*args, **kwargs)
        # collection_record, created = SampleCollection.objects.get_or_create(
        #             species=self
        #         )

        sequencing_record, created = Sequencing.objects.get_or_create(
                    species=self
                )

        assemblyproject_record, created = AssemblyProject.objects.get_or_create(
                    species=self
                )

        annotation_record, created = Annotation.objects.get_or_create(
                    species=self
                )

        cannotation_record, created = CommunityAnnotation.objects.get_or_create(
                    species=self
                )
        genometeam_record, created = GenomeTeam.objects.get_or_create(
                    species=self
                )
        

    class Meta:
        verbose_name_plural = 'species'
        #ordering = ['taxon_kingdom', 'taxon_phylum', 'taxon_class', 'taxon_order','taxon_family','taxon_genus','scientific_name']
        ordering = ['scientific_name']

    # def get_tags(self):
    #     return "; ".join([t.tag for t in self.tags.all()])
    # get_tags.short_description = "Tags"

    def get_absolute_url(self):
        return reverse('species_detail', args=[self.pk])

    def __str__(self):
        return self.scientific_name or str(self.listed_species)
        #return self.scientific_name +" (" + self.tolid_prefix + ")"

class CommonNames(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="Genus/species")
    name = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'common names'

    def __str__(self):
        return self.name or str(self.id)

class Synonyms(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="Genus/species")
    name = models.CharField(max_length=201, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'synonyms'

    def __str__(self):
        return self.name

class Affiliation(models.Model):
    affiliation = models.CharField(max_length=500, null=True, blank=True, unique=True)

    class Meta:
        verbose_name_plural = 'affiliations'

    def __str__(self):
        return self.affiliation or str(self.id)

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
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    def get_roles(self):
        if (self.roles.all()):
            return "; ".join([r.description for r in self.roles.all()])
        else:
            return "other"
    get_roles.short_description = "Roles"

    def get_affiliations(self):
        if (self.affiliation.all()):

            return "; ".join([str(a.affiliation or 'no affiliation') for a in self.affiliation.all()])
        else:
            return "no affiliation"
    get_affiliations.short_description = "Affiliations"
    
    def get_absolute_url(self):
        return reverse('user_profile', args=[str(self.pk)])

    def __str__(self):
        return self.first_name + " " + self.last_name or str(self.id)

    def save(self, *args, **kwargs):
        super(UserProfile, self).save(*args, **kwargs)
        send_mail(
            '[ERGA] New user, '+ self.first_name + " " + self.last_name +', has registered in ERGA-Stream',
            'name: '+ self.first_name +" "+self.last_name +"\nemail: "+self.user.email+"\naffiliations: "+self.get_affiliations()+"\nroles: "+self.get_roles()+"\nlead: "+str(self.lead)+"\n",
            'denovo@cnag.eu',
            ['denovo@cnag.eu'],
            fail_silently=True,
        )

class Person(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    affiliation = models.ManyToManyField(Affiliation,null=True, blank=True)
    orcid = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    email = models.EmailField(max_length=40, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'people'
    def get_absolute_url(self):
        return reverse('person_detail', args=[str(self.pk)])
    def __str__(self):
        return self.name  or str(self.id)

class AnnotationTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='annotation_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'annotation teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('annotation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class CommunityAnnotationTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='community_annotation_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'Community annotation teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('community_annotation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class BiobankingTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    institution = models.ManyToManyField(Affiliation)
    lead = models.ForeignKey(
        #UserProfile,
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='biobanking_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'biobanking teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('biobanking_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class AssemblyTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.SET_NULL, 
        related_name='assembly_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'assembly teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('assembly_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class CurationTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='curation_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'curation teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('curation_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class SequencingTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='sequencing_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    gal_name = models.CharField(max_length=100,null=True, blank=True)

    class Meta:
        verbose_name_plural = 'sequencing teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('sequencing_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class HiCTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='hic_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    gal_name = models.CharField(max_length=100,null=True, blank=True)

    class Meta:
        verbose_name_plural = 'hic teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('hic_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)
    
class ExtractionTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='extraction_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'extraction teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('extraction_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class CollectionTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile, 
        null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='collection_team_lead'
    )
    members = models.ManyToManyField(UserProfile, null=True, blank=True) 
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'collection teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('collection_team_detail', args=[str(self.pk)])

    def __str__(self):
        # return str(self.lead) or self.name or str(self.id)
        return self.name or str(self.id)


class TaxonomyTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,
        null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='taxonomy_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'taxonomy teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('taxonomy_team_detail', args=[str(self.pk)])

    def __str__(self):
        #return str(self.lead) or self.name or str(self.id)
        return self.name or str(self.id)

class SampleHandlingTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='sample_handling_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'sample handling teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('sample_handling_team_detail', args=[str(self.pk)])

    def __str__(self):
        # return str(self.lead) or self.name or str(self.id)
        return self.name or str(self.id)

class VoucheringTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.SET_NULL, 
        related_name='vouchering_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'vouchering teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('vouchering_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class BarcodingTeam(models.Model):
    name = models.CharField(max_length=100,unique=True)
    lead = models.ForeignKey(
        UserProfile,null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='barcoding_team_lead'
    )
    members = models.ManyToManyField(UserProfile,null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'barcoding teams'
        ordering = ("name",)

    def get_absolute_url(self):
        return reverse('barcoding_team_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class Author(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name="author")
    role = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return self.author.first_name + " " + self.author.last_name

class GenomeTeam(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",related_name='gt_rel')
    sample_handling_team = models.ForeignKey(SampleHandlingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sample handling team")
    sample_coordinator = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sample_coordinator")
    coordinator = models.ForeignKey(Person,on_delete=models.SET_NULL, null=True, blank=True, verbose_name="coordinator")
    collection_team = models.ForeignKey(CollectionTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="collection team")
    taxonomy_team = models.ForeignKey(TaxonomyTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="taxonomy team")
    vouchering_team = models.ForeignKey(VoucheringTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="vouchering team")
    barcoding_team = models.ForeignKey(BarcodingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="barcoding team")
    biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
    extraction_team = models.ForeignKey(ExtractionTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="nucleic acid extraction team")
    sequencing_team = models.ForeignKey(SequencingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="sequencing team")
    hic_team = models.ForeignKey(HiCTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Hi-C team")
    assembly_team = models.ForeignKey(AssemblyTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="assembly team")
    community_annotation_team = models.ForeignKey(CommunityAnnotationTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="community annotation team")
    annotation_team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="annotation team")
    class Meta:
        verbose_name_plural = 'genome teams'
    
    def __str__(self):
        return self.species.scientific_name or str(self.id)

class Subproject(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = 'subprojects'

    def get_absolute_url(self):
        return reverse('subproject_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name
    
class Task(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subproject = models.ForeignKey(Subproject,on_delete=models.CASCADE, default=1, verbose_name="subproject", null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'tasks'

    def get_absolute_url(self):
        return reverse('task_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name
    
class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'countries'
    
    def get_absolute_url(self):
        return reverse('country_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name

BARCODING_STATUS_CHOICES = (
    ('DNA_BARCODING_TO_BE_PERFORMED', 'DNA_BARCODING_TO_BE_PERFORMED'),
    ('DNA_BARCODING_COMPLETED', 'DNA_BARCODING_COMPLETED'),
    ('DNA_BARCODING_EXEMPT', 'DNA_BARCODING_EXEMPT'),
    ('DNA_BARCODING_FAILED', 'DNA_BARCODING_FAILED')
)

class SampleCollection(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",unique=True,related_name='collection_rel')
    #team = models.ForeignKey(CollectionTeam, on_delete=models.SET_NULL, null=True, verbose_name="collection team", blank=True)
    copo_status = models.CharField(max_length=20, help_text='COPO status', choices=COPO_STATUS_CHOICES, default=COPO_STATUS_CHOICES[0][0])
    #genomic_sample_status = models.CharField(max_length=20, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    #rna_sample_status = models.CharField(max_length=20, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    #hic_sample_status = models.CharField(max_length=12, help_text='Status', choices=COLLECTION_STATUS_CHOICES, default=COLLECTION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    # ship_date = models.DateTimeField(verbose_name="Date shipped", editable=True, null=True, blank=True, default=None)
    subproject = models.ManyToManyField(Subproject,default=[0],blank=True,null=True)#default=1
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, verbose_name="Task", null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, verbose_name="Country", null=True, blank=True)
    sample_provider_name = models.CharField(max_length=100, null=True, blank=True)
    sample_provider_email = models.CharField(max_length=150, null=True, blank=True)
    mta1 =  models.BooleanField(default=False, verbose_name="MTA 1: Seq Centers")
    mta2 =  models.BooleanField(default=False, verbose_name="MTA 2: LIB leftovers")
    barcoding_status = models.CharField(max_length=30, help_text='Barcoding Status', choices=BARCODING_STATUS_CHOICES, default=BARCODING_STATUS_CHOICES[0][0])
    barcoding_results = models.CharField(max_length=200, null=True, blank=True)
    collection_forecast = models.DateField(blank=True,null=True)
    deadline_sampling = models.DateField(blank=True,null=True)
    deadline_manifest_sharing = models.DateField(blank=True,null=True)
    deadline_manifest_acceptance = models.DateField(blank=True,null=True)
    deadline_sample_shipment = models.DateField(blank=True,null=True)
    sampling_delay = models.BooleanField(default=False, verbose_name="Delayed sample")

    class Meta:
        verbose_name_plural = 'collection'
        ordering = ['species']

    __original_genomic_sample_status = None
    __original_rna_sample_status = None
    __original_copo_status = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.__original_genomic_sample_status = self.genomic_sample_status
        # self.__original_rna_sample_status = self.rna_sample_status
        self.__original_copo_status = self.copo_status

    def save(self, *args, **kwargs):
        # if (self.__original_genomic_sample_status != self.genomic_sample_status):
        #     stat_gsamp_records, created = StatusUpdate.objects.get_or_create(
        #         species=self.species,
        #         process='genomic_sample',
        #         status=self.genomic_sample_status
        #     )
        # if (self.__original_rna_sample_status != self.rna_sample_status):
        #     stat_rsamp_records, created = StatusUpdate.objects.get_or_create(
        #         species=self.species,
        #         process='rna_sample',
        #         status=self.rna_sample_status
        #     )
        if (self.__original_copo_status != self.copo_status):
            stat_g_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='copo_approval',
                status=self.copo_status
            )
        if settings.NOTIFICATIONS == True:

            if (self.__original_copo_status != 'Accepted'  and self.copo_status == 'Accepted'):
                myurl = settings.DEFAULT_DOMAIN + 'collection/?species='+str(self.species.pk)
                gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
                sequencing_team = gteam.sequencing_team
                if sequencing_team != None:
                    if sequencing_team.lead:
                        send_mail(
                            '[ERGA] Metadata for '+ self.species.scientific_name +' accepted in COPO.',
                            'Dear '+ sequencing_team.lead.first_name+",\n\nMetadata for one or more specimens of "+ self.species.scientific_name +" have been submitted and accepted by COPO. More info can be found here:\n" +myurl,
                            'denovo@cnag.eu',
                            [sequencing_team.lead.user.email],
                            fail_silently=True,
                        )
            if self.copo_status == 'Accepted':
                gteam = GenomeTeam.objects.get(species=self.species)
                sh_team = SampleHandlingTeam.objects.filter(genometeam=gteam).first()
                if sh_team:
                    for m in sh_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='sample handling'
                        )
                tax_team = TaxonomyTeam.objects.filter(genometeam=gteam).first()
                if tax_team:
                    for m in tax_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='taxonomic identification'
                        )
                
                col_team = CollectionTeam.objects.filter(genometeam=gteam).first()
                if col_team:
                    for m in col_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='sample collection'
                        )
                
                bb_team = BiobankingTeam.objects.filter(genometeam=gteam).first()
                if bb_team:
                    for m in bb_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='biobanking'
                        )
                
                v_team = VoucheringTeam.objects.filter(genometeam=gteam).first()
                if v_team:
                    for m in v_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='vouchering'
                        )
                
                bc_team = BarcodingTeam.objects.filter(genometeam=gteam).first()
                if bc_team:
                    for m in bc_team.members.all():
                        species_authors, created = Author.objects.get_or_create(
                            species=self.species,
                            author=m,
                            role='barcoding'
                        )

        super(SampleCollection, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('collection_list', args=[self.species])

    def __str__(self):
        return self.species.scientific_name  or str(self.id)


@receiver(models.signals.post_delete, sender=SampleCollection)
def do_nothing(sender, *args, **kwargs):
    pass

class Specimen(models.Model):
    specimen_id = models.CharField(max_length=100, help_text='Internal Specimen ID', db_index=True)
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, related_name='specimen_rel', verbose_name="species",null=True, blank=True, db_index=True)
    tolid = models.CharField(max_length=20, help_text='Registered ToLID for the Specimen', null=True, blank=True)
    biosampleAccession = models.CharField(max_length=20, help_text='BioSample Accession', null=True, blank=True, verbose_name="Specimen BioSample")
    collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection", db_index=True)
    sample_coordinator = models.CharField(max_length=120, help_text='Sample coordinator', null=True, blank=True)
    tissue_removed_for_biobanking = models.BooleanField(default=False)
    tissue_voucher_id_for_biobanking = models.CharField(max_length=500, null=True, blank=True)
    proxy_tissue_voucher_id_for_biobanking = models.CharField(max_length=500, null=True, blank=True)
    tissue_for_biobanking = models.CharField(max_length=100, null=True, blank=True)
    dna_removed_for_biobanking = models.BooleanField(default=False)
    dna_voucher_id_for_biobanking = models.CharField(max_length=200, null=True, blank=True)
    voucher_id = models.CharField(max_length=200, help_text='Voucher ID', null=True, blank=True)
    proxy_voucher_id = models.CharField(max_length=200, help_text='Proxy voucher ID', null=True, blank=True)
    voucher_link = models.CharField(max_length=200, null=True, blank=True)
    proxy_voucher_link = models.CharField(max_length=200, null=True, blank=True)
    voucher_institution = models.CharField(max_length=200, null=True, blank=True)
    biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
    nagoya_statement = models.ForeignKey(Statement, on_delete=models.SET_NULL, verbose_name="legal statement",null=True, blank=True)
    ircc = models.URLField(max_length = 400, null=True, blank=True, verbose_name="IRCC")
    def get_absolute_url(self):
        return reverse('specimen_list', args=[str(self.pk)])
    
    def __str__(self):
        return self.tolid or self.specimen_id or str(self.id)

class FromManifest(models.Model):
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, related_name="manifest_roles_rel", verbose_name="specimen")
    collector = models.ManyToManyField(Person, null=True, blank=True, related_name="collector_rel")
    preserver = models.ManyToManyField(Person, null=True, blank=True, related_name="preserver_rel")
    identifier = models.ManyToManyField(Person, null=True, blank=True, related_name="identifier_rel")
    coordinator = models.ManyToManyField(Person, null=True, blank=True, related_name="coordinator_rel")
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    class Meta:
        verbose_name_plural = 'manifest roles'

    def get_absolute_url(self):
        return reverse('from_manifest_detail', args=[str(self.specimen.pk)])

    def __str__(self):
        # return str(self.lead) or self.name or str(self.id)
        return self.specimen.tolid

LEFTOVER_CHOICES = (
    ('None', 'None'),
    ('DNA', 'DNA'),
    ('Tissue', 'Tissue'),
    ('Both', 'Both')
) 
class Sample(models.Model):
    copo_id = models.CharField(max_length=30, help_text='COPO ID', null=True, blank=True, verbose_name="CopoID")
    biosampleAccession = models.CharField(max_length=20, help_text='BioSample Accession', null=True, blank=True, verbose_name="BioSample")
    sampleDerivedFrom = models.CharField(max_length=20, help_text='BioSample Derived From', null=True, blank=True, verbose_name="SampleDerivedFrom")
    sampleSameAs = models.CharField(max_length=20, help_text='BioSample Same As', null=True, blank=True, verbose_name="SampleSameAs")
    barcode = models.CharField(max_length=50, help_text='Tube barcode', null=True, blank=True)
    # collection = models.ForeignKey(SampleCollection, on_delete=models.CASCADE, verbose_name="Collection")
    purpose_of_specimen = models.CharField(max_length=30, help_text='Purpose', null=True, blank=True)
    gal = models.CharField(max_length=120, help_text='GAL', null=True, blank=True, verbose_name="GAL")
    gal_sample_id = models.CharField(max_length=200, help_text='GAL Sample ID', null=True, blank=True)
    collector_sample_id = models.CharField(max_length=200, help_text='Collector Sample ID', null=True, blank=True)
    tube_or_well_id = models.CharField(max_length=200, help_text='Tube or Well ID', null=True, blank=True)
    corrected_id = models.CharField(max_length=200, help_text='Corrected ID', null=True, blank=True)
    copo_date = models.CharField(max_length=50, help_text='COPO Time Updated', null=True, blank=True, verbose_name="date")
    #copo_update_date = models.CharField(max_length=30, help_text='COPO Time Updated', null=True, blank=True, verbose_name="date")
    copo_status = models.CharField(max_length=30, help_text='COPO Status', null=True, blank=True, verbose_name="Status")
    specimen = models.ForeignKey(Specimen, on_delete=models.CASCADE, verbose_name="Specimen",null=True, blank=True)
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species",null=True, blank=True)
    leftover = models.CharField(max_length=20, help_text='Leftover sample', choices=LEFTOVER_CHOICES, default=LEFTOVER_CHOICES[0][0])
    leftover_biobanking_team = models.ForeignKey(BiobankingTeam, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="biobanking team")
    date_sent = models.DateField(blank=True,null=True)
    date_received = models.DateField(blank=True,null=True)

    def get_absolute_url(self):
        return reverse('sample_detail', args=[str(self.pk)])

    def __str__(self):
        return self.biosampleAccession or self.collector_sample_id or str(self.id)
 
class Recipe(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Recipe name")
    ont_target = models.BigIntegerField(null=True, blank=True, verbose_name="ONT target")
    hifi_target = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi target")
    hic_target = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C target")
    short_target = models.BigIntegerField(null=True, blank=True, verbose_name="Short read target")
    rna_target = models.BigIntegerField(null=True, blank=True, verbose_name="RNA-seq PE target")
        
    class Meta:
        verbose_name_plural = 'recipes'

    def get_absolute_url(self):
        return reverse('recipe_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name or str(self.id)

class Phase(models.Model):
    name = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name_plural = 'phases'

    def get_absolute_url(self):
        return reverse('phase_detail', args=[str(self.pk)])
    
    def __str__(self):
        return self.name

class Sequencing(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, related_name='sequencing_rel', verbose_name="species")
    phase = models.ForeignKey(Phase, on_delete=models.SET_NULL, verbose_name="Phase", null=True)
    #team = models.ForeignKey(SequencingTeam, on_delete=models.SET_NULL, null=True, verbose_name="sequencing team")
    long_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    short_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    hic_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    rna_seq_status = models.CharField(max_length=20, help_text='Status', choices=SEQUENCING_STATUS_CHOICES, default='Waiting')
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, to_field='name', verbose_name="Recipe", null=True, blank=True)
    #recipe = models.ForeignKey(Recipe, on_delete=models.SET_NULL, to_field='name', default='HiFi25', verbose_name="Recipe", null=True, blank=True)
    
    __original_long_seq_status = None
    __original_short_seq_status = None
    __original_hic_seq_status = None
    __original_rna_seq_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_long_seq_status = self.long_seq_status
        self.__original_short_seq_status = self.short_seq_status
        self.__original_hic_seq_status = self.hic_seq_status
        self.__original_rna_seq_status = self.rna_seq_status

    def save(self, *args, **kwargs):
        if self.long_seq_status != "Received" and self.long_seq_status != "Waiting":
            #species = TargetSpecies.objects.get(species=self.species)
            if gss_rank[self.species.goat_sequencing_status]<4:
                self.species.goat_sequencing_status = "data_generation" 
                self.species.save()
        if self.short_seq_status != "Received" and self.short_seq_status != "Waiting":
            #species = TargetSpecies.objects.get(species=self.species)
            if gss_rank[self.species.goat_sequencing_status]<4:
                self.species.goat_sequencing_status = "data_generation" 
                self.species.save()
        if self.hic_seq_status != "Received" and self.hic_seq_status != "Waiting":
            #species = TargetSpecies.objects.get(species=self.species)
            if gss_rank[self.species.goat_sequencing_status]<4:
                self.species.goat_sequencing_status = "data_generation" 
                self.species.save()
        if (self.__original_long_seq_status != self.long_seq_status):
            #get species and set goat_sequencing_status to "data_generation"
            stat_g_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='long_seq',
                status=self.long_seq_status
            )
        if (self.__original_short_seq_status != self.short_seq_status):
            #get species and set goat_sequencing_status to "data_generation"
            if self.short_seq_status != "Received" and self.short_seq_status != "Waiting":
                #species = TargetSpecies.objects.get(species=self.species)
                if gss_rank[self.species.goat_sequencing_status]<4:
                    self.species.goat_sequencing_status = "data_generation" 
                    #species.save()
            stat_g_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='short_seq',
                status=self.short_seq_status
            )
        if (self.__original_hic_seq_status != self.hic_seq_status):
            #get species and set goat_sequencing_status to "data_generation"
            if self.hic_seq_status != "Received" and self.hic_seq_status != "Waiting":
                #species = TargetSpecies.objects.get(species=self.species)
                if gss_rank[self.species.goat_sequencing_status]<4:
                    self.species.goat_sequencing_status = "data_generation" 
                    #species.save()
            stat_h_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='hic_seq',
                status=self.hic_seq_status
            )
        if (self.__original_rna_seq_status != self.rna_seq_status):
            stat_r_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='rna_seq',
                status=self.rna_seq_status
            )
        if settings.NOTIFICATIONS == True:

            if ((self.__original_long_seq_status != 'Done' and self.__original_long_seq_status != 'Submitted') and (self.long_seq_status == 'Done' or self.long_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
                assembly_team = gteam.assembly_team
                if assembly_team != None:
                    if assembly_team.lead:
                        send_mail(
                            '[ERGA] Long read genomic sequencing for '+ self.species.scientific_name +'is done',
                            'Dear '+ assembly_team.lead.first_name+",\n\nLong-read genomic sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                            'denovo@cnag.eu',
                            [assembly_team.lead.user.email],
                            fail_silently=True,
                        )

            if ((self.__original_short_seq_status != 'Done' and self.__original_short_seq_status != 'Submitted') and (self.short_seq_status == 'Done' or self.short_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
                assembly_team = gteam.assembly_team
                if assembly_team != None:
                    if assembly_team.lead:
                        send_mail(
                            '[ERGA] Genomic sequencing for '+ self.species.scientific_name +'is done',
                            'Dear '+ assembly_team.lead.first_name+",\n\nShort-read genomic sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                            'denovo@cnag.eu',
                            [assembly_team.lead.user.email],
                            fail_silently=True,
                        )

            if ((self.__original_hic_seq_status != 'Done' and self.__original_hic_seq_status != 'Submitted') and (self.hic_seq_status == 'Done' or self.hic_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
                assembly_team = gteam.assembly_team
                if assembly_team != None:
                    if assembly_team.lead:
                        send_mail(
                            '[ERGA] Hi-C sequencing for '+ self.species.scientific_name +'is done',
                            'Dear '+ assembly_team.lead.first_name+",\n\nHi-C sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                            'denovo@cnag.eu',
                            [assembly_team.lead.user.email],
                            fail_silently=True,
                        )

            if ((self.__original_rna_seq_status != 'Done' and self.__original_rna_seq_status != 'Submitted') and (self.rna_seq_status == 'Done' or self.rna_seq_status == 'Submitted')):
                myurl = settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(self.species.pk)
                gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
                community_annotation_team = gteam.community_annotation_team
                if community_annotation_team != None:
                    if community_annotation_team.lead:
                        send_mail(
                            '[ERGA] RNA sequencing for '+ self.species.scientific_name +'is done',
                            'Dear '+ community_annotation_team.lead.first_name+",\n\nRNA sequencing for "+ self.species.scientific_name + " is done. More info can be found here:\n" +myurl,
                            'denovo@cnag.eu',
                            [community_annotation_team.lead.user.email],
                            fail_silently=True,
                        )

        if self.__original_long_seq_status == 'Waiting' and self.long_seq_status != 'Waiting':
            gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
            team = gteam.sequencing_team
            if team != None:
                for m in team.members.all():
                    species_authors, created = Author.objects.get_or_create(
                        species=self.species,
                        author=m,
                        role='sequencing'
                    )
        if (self.__original_long_seq_status != self.long_seq_status):
            stat_gseq_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='long_seq',
                status=self.long_seq_status
            )

        if self.__original_short_seq_status == 'Waiting' and self.short_seq_status != 'Waiting':
            gteam, created = GenomeTeam.objects.get_or_create(species=self.species)
            team = gteam.sequencing_team
            if team != None:
                for m in team.members.all():
                    species_authors, created = Author.objects.get_or_create(
                        species=self.species,
                        author=m,
                        role='sequencing'
                    )
        if (self.__original_short_seq_status != self.short_seq_status):
            stat_gseq_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='short_seq',
                status=self.short_seq_status
            )
        if (self.__original_rna_seq_status != self.rna_seq_status):
            stat_rseq_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='rna_seq',
                status=self.rna_seq_status
            )
        if (self.__original_hic_seq_status != self.hic_seq_status):
            stat_hicseq_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='hic_seq',
                status=self.hic_seq_status
            )
        super(Sequencing, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('sequencing_list', args=[str(self.pk)])

    class Meta:
        verbose_name_plural = 'sequencing'

    def __str__(self):
        return self.species.scientific_name or str(self.id)

@receiver(models.signals.post_delete, sender=Sequencing)
def do_nothing(sender, *args, **kwargs):
    pass

class Reads(models.Model):
    project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    #ont_yield = models.BigIntegerField(null=True, blank=True, verbose_name="ONT yield")
    #hifi_yield = models.BigIntegerField(null=True, blank=True, verbose_name="HiFi yield")
    #hic_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Hi-C yield")
    #short_yield = models.BigIntegerField(null=True, blank=True, verbose_name="Short read yield")
    #rnaseq_pe = models.BigIntegerField(null=True, blank=True, verbose_name="RNA-seq yield (PE)")
    ont_ena = models.CharField(max_length=12, null=True, blank=True, verbose_name="ONT Accession")
    hifi_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="HiFi Accession")
    hic_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Hi-C Accession")
    short_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Short read Accession")
    rnaseq_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="RNAseq Accession")
    study_accession = models.CharField(max_length=12, null=True, blank=True, verbose_name="Study")
    
    def get_absolute_url(self):
        return reverse('reads_list', args=[str(self.project)])

    class Meta:
        verbose_name_plural = 'reads'

    def __str__(self):
        return self.project.species.scientific_name or str(self.id)

#center scientific_name tolid_prefix recipe read_type  status notes sample_tube_or_well_id instrument_model yield forward_file_name forward_file_md5 reverse_file_name reverse_file_md5 native native_md5sum experiment_attributes run_attributes nominal_length nominal_sdev library_construction_protocol	      
class Run(models.Model):
    project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    read_type = models.CharField(max_length=15, help_text='Read type', choices=READ_TYPES, default=READ_TYPES[0][0])
    seq_yield = models.BigIntegerField(null=True, blank=True, verbose_name="yield")
    forward_filename = models.CharField(max_length=200, default='', help_text='Forward read filename')
    forward_md5sum = models.CharField(max_length=32, null=True, blank=True, help_text='Forward read md5sum')
    reverse_filename = models.CharField(max_length=200, null=True, blank=True, help_text='Forward read filename')
    reverse_md5sum = models.CharField(max_length=32, null=True, blank=True, help_text='Forward read md5sum')
    native_filename = models.CharField(max_length=200, null=True, blank=True, help_text='Forward read filename')
    native_md5sum = models.CharField(max_length=32, null=True, blank=True, help_text='Forward read md5sum')
    #sample = models.ForeignKey(Sample, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Sample")
    sample = models.CharField(max_length=200, null=True, blank=True, help_text='Sample(s)')
    tube_or_well_id = models.CharField(max_length=32, null=True, blank=True, help_text='Tube or Well ID')
    reads = models.ForeignKey(Reads, related_name="run_set", related_query_name="run_set", null=True, blank=True, on_delete=models.CASCADE, verbose_name="Reads aggregate view")

    class Meta:
        verbose_name_plural = 'runs'

    def __str__(self):
        return self.project.species.scientific_name + " " + self.read_type + " " + self.forward_filename or str(self.id)

class EnaRun(models.Model):
    project = models.ForeignKey(Sequencing, on_delete=models.CASCADE, verbose_name="Sequencing project")
    read_type = models.CharField(max_length=15, help_text='Read type', choices=READ_TYPES, default=READ_TYPES[0][0])
    seq_yield = models.BigIntegerField(null=True, blank=True, verbose_name="yield")
    biosample_accession = models.CharField(max_length=12, null=True, blank=True, verbose_name='Biosample Accession')
    run_accesssion = models.CharField(max_length=12, null=True, blank=True, verbose_name='Run Accession')
    experiment_accesssion = models.CharField(max_length=12, null=True, blank=True, verbose_name='Experiment Accession')
    study_accesssion = models.CharField(max_length=12, null=True, blank=True, verbose_name='Study Accession')
    reads = models.ForeignKey(Reads, related_name="ena_run_set", related_query_name="ena_run_set", null=True, blank=True, on_delete=models.CASCADE, verbose_name="Reads aggregate view")

    class Meta:
        verbose_name_plural = 'ena_runs'

    def __str__(self):
        return self.project.species.scientific_name + " " + self.read_type + " " + self.run_accesssion or str(self.id)

class Curation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(CurationTeam, on_delete=models.SET_NULL, null=True, verbose_name="curation team")
    status = models.CharField(max_length=20, help_text='Status', choices=CURATION_STATUS_CHOICES, default=CURATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    class Meta:
        verbose_name_plural = 'curation'

    def __str__(self):
        return self.species.tolid_prefix or str(self.id)

class CommunityAnnotation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, verbose_name="annotation team")
    status = models.CharField(max_length=20, help_text='Status', choices=ANNOTATION_STATUS_CHOICES, default=ANNOTATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)

    __original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status
 
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
        if (self.__original_status != self.status):
            stat_cannot_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='community_annotation',
                status=self.status
            )
        super(CommunityAnnotation, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.species.scientific_name or str(self.id)
    
class Annotation(models.Model):
    species = models.OneToOneField(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(AnnotationTeam, on_delete=models.SET_NULL, null=True, verbose_name="annotation team")
    status = models.CharField(max_length=20, help_text='Status', choices=ANNOTATION_STATUS_CHOICES, default=ANNOTATION_STATUS_CHOICES[0][0])
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    ensembl = models.URLField(max_length = 400, null=True, blank=True, verbose_name="Ensembl Rapid")

    __original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status

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
        if (self.__original_status != self.status):
            stat_annot_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='annotation',
                status=self.status
            )
        super(Annotation, self).save(*args, **kwargs)
 
    class Meta:
        verbose_name_plural = 'annotation'

    def __str__(self):
        return self.species.scientific_name or str(self.id)

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
    species = models.OneToOneField(TargetSpecies, related_name='assembly_rel', on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(AssemblyTeam, on_delete=models.SET_NULL, null=True, verbose_name="assembly team")
    status = models.CharField(max_length=12, help_text='Status', choices=ASSEMBLY_STATUS_CHOICES, default=ASSEMBLY_STATUS_CHOICES[0][0])
    genome_size_estimate = models.BigIntegerField(null=True, blank=True, verbose_name="Genome Size Estimate")
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    assembly_rank = models.IntegerField(null=True, blank=True, default=0)
    class Meta:
        verbose_name_plural = 'assembly projects'

    __original_status = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__status = self.status

    def save(self, *args, **kwargs):
        if self.status != "Waiting":
            #species = TargetSpecies.objects.get(species=self.species)
            if gss_rank[self.species.goat_sequencing_status]<6:
                if self.status == "Submitted":
                    self.species.goat_sequencing_status = "insdc_open" 
                    self.species.save()
                else:
                    self.species.goat_sequencing_status = "in_assembly" 
                    self.species.save()
        if self.status != 'Waiting':
            gteam = GenomeTeam.objects.get(species=self.species)
            team = AssemblyTeam.objects.get(genometeam=gteam)
            for m in team.members.all():
                species_authors, created = Author.objects.get_or_create(
                    species=self.species,
                    author=m,
                    role='assembly'
                )
        if (self.__original_status != self.status):
            stat_assm_records, created = StatusUpdate.objects.get_or_create(
                species=self.species,
                process='assembly',
                status=self.status
            )

        if not self.genome_size_estimate:
            self.genome_size_estimate = self.species.genome_size
        self.assembly_rank = assembly_rank[self.status]
        super(AssemblyProject, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('assembly_project_list', args=[str(self.pk)])

    def __str__(self):
        return self.species.scientific_name or str(self.id)

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
        return reverse('assembly_pipeline_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name + "." + self.version or str(self.id)

class BUSCOdb(models.Model):
    db = models.CharField(max_length=60, db_index=True)
    class Meta:
        verbose_name_plural = 'BUSCO dbs'

    def __str__(self):
        return self.db or str(self.id)

class BUSCOversion(models.Model):
    version = models.CharField(max_length=10, db_index=True)
    class Meta:
        verbose_name_plural = 'BUSCO versions'

    def __str__(self):
        return self.version or str(self.id)

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return "user_{0}/{1}".format(instance.project, filename)

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
    report = models.URLField(max_length = 400, null=True, blank=True)
    accession = models.CharField(max_length=12,null=True, blank=True, verbose_name="Project Accession")
    gca = models.CharField(max_length=20,null=True, blank=True, verbose_name="GCA")
    #pretext = models.FileField(upload_to=user_directory_path, max_length = 400, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'assemblies'

    def __str__(self):
        return self.project.species.tolid_prefix + '.' + self.type or str(self.id)

class StatusUpdate(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="species")
    #team = models.ForeignKey(AssemblyTeam, on_delete=models.SET_NULL, null=True, verbose_name="assembly team")
    process = models.CharField(max_length=30, help_text='Process')
    status = models.CharField(max_length=20, help_text='Status')
    note = models.CharField(max_length=300, help_text='Notes', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add= True)

    class Meta:
        verbose_name_plural = 'status updates'

    # def __str__(self):
    #     return self.id

class SpeciesUpload(models.Model):
    file = models.FileField(upload_to='uploaded_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)