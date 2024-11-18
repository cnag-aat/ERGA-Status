# tables.py
import django_tables2 as tables
from django_tables2.utils import A
from .models import *
import re
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import format_html
from django.urls import reverse
from status.models import *
from django.conf import settings

class SummingColumn(tables.Column):
    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)

class SummingGBColumn(tables.Column):
    def render_footer(self, bound_column, table):
        return "{:.3f}".format(sum(bound_column.accessor.resolve(row) for row in table.data)/1000000000)
        #return sum(bound_column.accessor.resolve(row) for row in table.data)/1000000000
      
class OverviewTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    genome_size_update = SummingGBColumn(verbose_name='Span'
        #footer=lambda table: sum(x["genome_size_update"] for x in table.data)
    )
    tasks = tables.ManyToManyColumn(accessor='collection_rel',verbose_name='Tasks') #accessor='collection_rel__task__short_name'
    seq_center = tables.Column(accessor='gt_rel__sequencing_team__name',verbose_name='Center')
    copo_status = tables.Column(verbose_name='COPO',attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    long_seq_status = tables.Column(accessor='sequencing_rel.long_seq_status',verbose_name='ONT/HiFi WGS',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    short_seq_status = tables.Column(accessor='sequencing_rel.short_seq_status',verbose_name='Illumina WGS',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    hic_seq_status = tables.Column(accessor='sequencing_rel.hic_seq_status',verbose_name='Hi-C',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    rna_seq_status = tables.Column(accessor='sequencing_rel.rna_seq_status',verbose_name='RNA-Seq',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    assembly_status = tables.Column(accessor='assembly_rel__status',verbose_name='Assembly',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    #community_annotation_status = tables.Column(accessor='communityannotation.status',verbose_name='Community Annotation',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    annotation_status = tables.Column(accessor='annotation.status',verbose_name='Annotation',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    tolid_prefix = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    scientific_name = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    log = tables.TemplateColumn('<a href="' + settings.DEFAULT_DOMAIN + 'log/?species={{record.id}}"><i class="fas fa-history"></i></a>',empty_values=(), verbose_name='log',orderable=False)
    #attrs={"td": {"class": "overview-table"}}

    goat_sequencing_status = tables.Column(verbose_name="GoaT Status",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    assembly_rank = tables.Column(accessor='assembly_rel__assembly_rank',verbose_name='Assembly level')
    
    def render_tasks(self, value, record):
        clist = ""
        cfirst = True

        collections = list(value.all())
        print(str(collections))
        for c in collections:
            if not cfirst:
                clist += "<br />"
            else:
                cfirst = False
            #print c.task.short_name
            if c is not None:
                if c.task is not None:
                    print(c.task)
                    print(c.task.short_name)
                    clist += str(c.task.short_name) 

        return mark_safe(clist)
    
    #targetspecies=TargetSpecies.objects.get(=pk)
    # def render_collection_status(self, value):
    #     return mark_safe('<a href="'+
    #         url('collection_list',kwargs={'scientific_name': record.scientific_name})
    #         +'"><span class="'+escape(value)+'">'+escape(value)+'</span>')
    # def render_log(self, value, record):
    #     if(record.scientific_name):
    #         html = '<a href="/erga-stream-dev/log/?species='+str(record.scientific_name.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
    #         return mark_safe(html) 
    #     else:
    #         return ''
    # def render_seq_center(self, value, record):
    #     url = reverse('species_detail',kwargs={'pk': record.pk})
    #     return format_html('<a href="{}">{}</a>',url, str(value))

    def render_genome_size_update(self, value, record):
        return "{:.3f}".format(value/1000000000)
    
    def render_scientific_name(self, value, record):
        url = reverse('species_detail',kwargs={'pk': record.pk})
        return format_html('<a href="{}">{}</a>',url, str(value))

        # if (str(value) == str(record.listed_species)):
        #     return format_html('<a href="{}">{}</a>',url, str(value))
        # else:
        #     return format_html('<a href="{}">{}</a>',url, str(value) + " (" + str(record.listed_species) + ")") #'<a href="{}/{}">{}</a>', 
    def value_scientific_name(self, value):
        return value
      
    def render_goat_sequencing_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'collection/?species='+str(record.pk)+'"><span class="status '+escape(value.replace(" ",''))+'">'+escape(value.replace("sample_",''))+'</span></a>'
        return mark_safe(html)

    def value_goat_sequencing_status(self, value):
        return value
        
    def render_copo_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'collection/?species='+str(record.pk)+'"><span class="status '+escape(value.replace(" ",''))+'">'+escape(value)+'</span></a>'

        # cs_string = ""
        # sFirst = True
        # for s in value.all():
        #     #html = '<a href="' + settings.DEFAULT_DOMAIN + 'collection/?species='+str(record.pk)+'"><span class="status '+escape(value.replace(" ",''))+'">'+escape(value)+'</span></a>'
        #     cs_string += html
        return mark_safe(html)

    def value_copo_status(self, value):
        return value

    # def render_hic_sample_status(self, value, record):
    #     html = '<a href="/erga-stream-dev/collection/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
    #     return mark_safe(html)

    def value_hic_sample_status(self, value):
        return value

    # def render_rna_sample_status(self, value, record):
    #     html = '<a href="/erga-stream-dev/collection/?species='+str(record.pk)+'"><span class="status '+escape(value.replace(" ",''))+'">'+escape(value)+'</span></a>'
    #     return mark_safe(html)

    # def value_rna_sample_status(self, value):
    #     return value

    def render_long_seq_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_long_seq_status(self, value):
        return value

    def render_short_seq_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_short_seq_status(self, value):
        return value
    
    def render_hic_seq_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_hic_seq_status(self, value):
        return value

    def render_rna_seq_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_rna_seq_status(self, value):
        return value
    
    def render_assembly_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'projects/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_assembly_status(self, value):
        return value

    # def render_curation_status(self, value, record):
    #     html = '<a href="/erga-stream-dev/curation/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
    #     return mark_safe(html)

    # def value_curation_status(self, value):
    #     return value

    def render_annotation_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'annotation/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_annotation_status(self, value):
        return value
    
    def render_community_annotation_status(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'community_annotation/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_community_annotation_status(self, value):
        return value
    # def render_submission_status(self, value, record):
    #     html = '<a href="/erga-stream-dev/submission/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
    #     return mark_safe(html)

    # def value_submission_status(self, value):
    #     return value

    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        # fields = ('tolid_prefix', 'scientific_name','genomic_sample_status','hic_sample_status','rna_sample_status','genomic_seq_status','hic_seq_status','rna_seq_status','assembly_status','curation_status','annotation_status','submission_status')
        fields = ('scientific_name','tolid_prefix','taxon_phylum','genome_size_update','tasks','seq_center','goat_sequencing_status','copo_status','long_seq_status','short_seq_status','hic_seq_status','rna_seq_status','assembly_status','annotation_status','assembly_rank','log')

class TargetSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    genome_size_update = SummingColumn(
        #footer=lambda table: sum(x["genome_size_update"] for x in table.data)
    )
    genome_size_update = SummingColumn(
        #footer=lambda table: sum(x["genome_size"] for x in table.data)
    )
    scientific_name = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    subspecies_rel = tables.ManyToManyColumn(verbose_name="Subspecies") #accessor='subspecies_rel.scientific_name',
    phase = tables.Column(accessor='sequencing_rel__phase',verbose_name="Phase")
    task = tables.Column(accessor='collection_rel__task',verbose_name="Task")
    country = tables.Column(accessor='collection_rel__country',verbose_name="Country")
    def render_scientific_name(self, value, record):
        url = reverse('species_detail',kwargs={'pk': record.pk})
        return format_html('<a href="{}">{}</a>',url, str(value))

    
        # url = reverse('species_detail',kwargs={'pk': record.pk})
        # if (str(value) == str(record.listed_species)):
        #     return format_html('<a href="{}">{}</a>',url, str(value))
        # else:
        #     return format_html('<a href="{}">{}</a>',url, str(value) + " (" + str(record.listed_species) + ")")
    #tolid_prefix = tables.Column(linkify=True)
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        #order_by = 'taxon_kingdom,taxon_phylum,taxon_class,taxon_order,taxon_family,taxon_genus,scientific_name' # use dash for descending order
        paginate = {"per_page": 100}
        fields = ('listed_species','scientific_name','taxon_id','subspecies_rel','genome_size','genome_size_update','phase','task','country','goat_target_list_status','goat_sequencing_status','ranking', 'iucn_code', 'iucn_url', 'c_value','ploidy','haploid_number','taxon_kingdom','taxon_phylum','taxon_class','taxon_order','taxon_family','taxon_genus')

class GoaTSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    #subproject = tables.ManyToManyColumn(accessor='collection_rel__subproject',verbose_name='subproject')
    subproject = tables.ManyToManyColumn(accessor='collection_rel',verbose_name='subproject')
    contributing_project_lab = tables.ManyToManyColumn(accessor='collection_rel',verbose_name='contributing_project_lab')
    scientific_name = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    taxon_id = tables.Column(verbose_name="ncbi_taxon_id")
    scientific_name = tables.Column(verbose_name="species")
    subspecies = tables.Column(verbose_name="subspecies")
    taxon_family = tables.Column(verbose_name="family")
    goat_target_list_status = tables.Column(verbose_name="target_list_status")
    goat_sequencing_status = tables.Column(verbose_name="sequencing_status")
    synonym = tables.Column(verbose_name="synonym")
    publication_id = tables.Column(verbose_name="publication_id")
    def render_contributing_project_lab(self, value, record):
        tasks = {sc.task.name for sc in value.all() if sc.task}
        return ';'.join(tasks)
        # tasks = {}
        # for sc in value.all():
        #     if sc.task is not None:
        #         tasks[sc.task.name]=1
        # return(';'.join(tasks.keys()))
    def render_subproject(self, value, record):
        subprojects = {sp.name for sc in value.all() for sp in sc.subproject.all() if sp}
        return ';'.join(subprojects)
        # subprojects = {}
        # for sc in value.all():
        #     for sp in sc.subproject.all():
        #         if sp is not None:
        #             subprojects[sp.name]=1
        # return(';'.join(subprojects.keys()))
     
    def render_goat_sequencing_status(self, value, record):
        return "none" if value in ["in_collection", "over_collection"] else value
        # if value == "in_collection" or value == "over_collection":
        #     return "none"
        # else:
        #     return value
    
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        #order_by = 'taxon_kingdom,taxon_phylum,taxon_class,taxon_order,taxon_family,taxon_genus,scientific_name' # use dash for descending order
        paginate = {"per_page": 100}
        fields = ('taxon_id', 'scientific_name','subspecies','taxon_family','goat_target_list_status','goat_sequencing_status','synonym','publication_id','subproject','contributing_project_lab')

class AssemblyTable(tables.Table):
    export_formats = ['csv', 'tsv']
    project = tables.LinkColumn('assembly_project_list')
    pipeline = tables.Column(linkify=True)
    #span = tables.Column(verbose_name="Span (Gb)")
    span = SummingColumn(verbose_name="Span (Gb)"
        #footer=lambda table: sum(x["genome_size"] for x in table.data)
    )
    contig_n50 = tables.Column(verbose_name="Contig N50 (Mb)")
    scaffold_n50 = tables.Column(verbose_name="Scaffold N50 (Mb)")
    accession = tables.Column(verbose_name="ENA Study")
    gca = tables.Column(verbose_name="GCA")
    assembly_team = tables.Column(accessor='project__species__gt_rel__assembly_team',linkify=True, verbose_name="Assembly Team")
    def render_scaffold_n50(self, value, record):
        return "{:.3f}".format(record.scaffold_n50/1000000)
    def render_contig_n50(self, value, record):
        return "{:.3f}".format(record.contig_n50/1000000)
    def render_span(self, value, record):
        return "{:.3f}".format(record.span/1000000000)
    def value_scaffold_n50(self, value):
        return value
    def value_contig_n50(self, value):
        return value
    def value_span_n50(self, value):
        return value
    def render_project(self, value, record):
        url = reverse('assembly_project_list')
        return format_html('<a href="{}?project={}">{}</a>', url, record.project.pk, value)
    def value_project(self, value):
        return value
    def render_accession(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)
    def render_gca(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)
    class Meta:
        model = Assembly
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id']

class AssemblyProjectTable(tables.Table):
    export_formats = ['csv', 'tsv']
    assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__gt_rel__assembly_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = AssemblyProject
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team','assemblies', 'note', 'status')

class SampleCollectionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    copo_status = tables.TemplateColumn('<span class="status {{record.copo_status|cut:" "}}">{{record.copo_status}}</span>',empty_values=(), verbose_name='COPO')
    # hic_sample_status = tables.TemplateColumn('<span class="{{record.hic_sample_status}}">{{record.hic_sample_status}}</span>',empty_values=(), verbose_name='HiC Sample')
    # rna_sample_status = tables.TemplateColumn('<span class="status {{record.rna_sample_status|cut:" "}}">{{record.rna_sample_status}}</span>',empty_values=(), verbose_name='RNA Sample')
    # species = tables.Column(linkify=True)
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=(), orderable=True)
    #species = tables.LinkColumn("species_detail", kwargs={"scientific_name": tables.A("species.scientific_name")}, empty_values=(), )
    #species = tables.TemplateColumn('<a href="{% url \'species_detail\' %}?pk={{record.species.pk}}">{{record.species.scientific_name}}</a>',empty_values=(), verbose_name='Species name')
    specimen = tables.TemplateColumn('<a href="{% url \'specimen_list\' %}?species={{record.species.pk}}">specimens</a>',empty_values=(), verbose_name='Specimen(s)', orderable=False)
    sample_handling_team = tables.Column(accessor='species__gt_rel__sample_handling_team',linkify=True, verbose_name="Sample Handling Team")
    #goat_sequencing_status = tables.Column(accessor='species__goat_sequencing_status', verbose_name="GoaT")
    goat_sequencing_status = tables.TemplateColumn('<span class="status {{record.species.goat_sequencing_status}}">{{record.species.goat_sequencing_status|cut:"sample_"}}</span>',empty_values=(), verbose_name='GoaT Status',orderable=False)
    subproject = tables.ManyToManyColumn(verbose_name="subproject")
    task = tables.Column(verbose_name="Task")
    taxon_id = tables.Column(accessor='species__taxon_id')
        
    def render_task(self, value, record):
        return value.short_name
    
    class Meta:
        model = SampleCollection
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id', 'sample_provider_name','sample_provider_email']
        #fields = ('species', 'team', 'specimens','note', 'genomic_sample_status','hic_sample_status','rna_sample_status')
        sequence = ('subproject','species',  'taxon_id','sample_handling_team', 'specimen','note', 'copo_status','goat_sequencing_status','...')

class SequencingTable(tables.Table):
    long_seq_status = tables.TemplateColumn('<span class="status {{record.long_seq_status}}">{{record.long_seq_status}}</span>',empty_values=(), verbose_name='Long-read Status')
    short_seq_status = tables.TemplateColumn('<span class="status {{record.short_seq_status}}">{{record.short_seq_status}}</span>',empty_values=(), verbose_name='Short-read Status')
    hic_seq_status = tables.TemplateColumn('<span class="status {{record.hic_seq_status}}">{{record.hic_seq_status}}</span>',empty_values=(), verbose_name='HiC Status')
    rna_seq_status = tables.TemplateColumn('<span class="status {{record.rna_seq_status}}">{{record.rna_seq_status}}</span>',empty_values=(), verbose_name='RNA Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__gt_rel__sequencing_team',linkify=True)
    reads = tables.TemplateColumn('<a href="{% url \'reads_list\' %}?project={{record.pk}}">reads</a>',empty_values=(), verbose_name='Reads')
    recipe = tables.TemplateColumn('<a href="{% url \'recipe_detail\'  record.recipe.pk %}">{{record.recipe}}</a>',empty_values=(), verbose_name='Recipe')
    def value_genomic_seq_status(self, value):
        return value
    def value_hic_seq_status(self, value):
        return value
    def value_rna_seq_status(self, value):
        return value

    class Meta:
        model = Sequencing
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'recipe', 'note', 'reads', 'long_seq_status','short_seq_status','hic_seq_status','rna_seq_status')

class RunTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    # assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    # status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    # species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    # team = tables.Column(accessor='species__genometeam__assembly_team',linkify=True)
    # biosample = tables.Column(accessor='tube_or_well_id__sample__biosampleAccession',verbose_name='BioSample accession')
    #reads = tables.Column(linkify=True)
    reads = tables.TemplateColumn('<a href="{% url \'reads_list\' %}?project={{record.project.pk}}">{{record.project}}</a>',empty_values=(), verbose_name='Data Summary')
    #sample = tables.Column(linkify=True)
    def value_status(self, value):
        return value

    class Meta:
        model = Run
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id']
        #fields = ('species', 'team','assemblies', 'note', 'status')

class EnaRunTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    # assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    # status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    # species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    # team = tables.Column(accessor='species__genometeam__assembly_team',linkify=True)
    # biosample = tables.Column(accessor='tube_or_well_id__sample__biosampleAccession',verbose_name='BioSample accession')
    #reads = tables.Column(linkify=True)
    reads = tables.TemplateColumn('<a href="{% url \'ena_reads_list\' %}?project={{record.project.pk}}">{{record.project}}</a>',empty_values=(), verbose_name='Data Summary')
    #sample = tables.Column(linkify=True)
    def value_status(self, value):
        return value

    class Meta:
        model = EnaRun
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id']
        #fields = ('species', 'team','assemblies', 'note', 'status')

class EnaReadsTable(tables.Table):
    project = tables.LinkColumn('sequencing_list')
    seq_center = tables.Column(accessor='project__species__gt_rel__sequencing_team__name',verbose_name='Center')
    ena_ont_yield = SummingColumn(verbose_name="ONT (Gb)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ena_ont_cov = tables.Column(verbose_name="ONT (x)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    #ont_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ena_hifi_yield = SummingColumn(verbose_name="HiFi (Gb)")
    ena_hifi_cov = tables.Column(verbose_name="HiFi (x)")
    #hifi_ena = tables.Column(verbose_name="ENA")
    ena_short_yield = SummingColumn(verbose_name="Illumina (Gb)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ena_short_cov = tables.Column(verbose_name="Illumina (x)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    #short_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ena_hic_yield = SummingColumn(verbose_name="Hi-C (Gb)")
    ena_hic_cov = tables.Column(verbose_name="Hi-C (x)")
    #hic_ena = tables.Column(verbose_name="ENA")
    ena_rnaseq_pe = SummingColumn(verbose_name="RNA-seq (MPE)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    runs = tables.TemplateColumn('<a href="{% url \'ena_runs_list\' %}?project={{record.project.pk}}&sort=read_type">{{record.project}}</a>',empty_values=(), verbose_name='Runs')

    def render_study_accession(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_project(self, value, record):
        url = reverse('sequencing_list')
        return format_html('<a href="{}?project={}">{}</a>', url, record.project.pk, value)

    def value_project(self, value):
        return value

    def render_ena_hifi_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe):
            if(rs.recipe.hifi_target == 0):
                if(int(value)>0):
                    css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'
            else:
                if (rs.recipe.hifi_target >  0):
                    threshmet = int(value)/(rs.recipe.hifi_target * rs.species.genome_size_update)
                    css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
                    if(threshmet > 0.25):
                        css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
                    if(threshmet > 0.5):
                        css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
                    if(threshmet > 0.75):
                        css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
                    if(threshmet >= 1.0):
                        css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        #cov = int(value)/rs.species.genome_size_update_update if int(value) else ""
        if (value == 0 or rs.recipe.hifi_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_ena_hifi_yield(self, value):
        if value is not None:
            return value
        else:
            return 0

    def render_ena_hic_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe):
            if(rs.recipe.hic_target == 0):
                if(int(value)>0):
                    css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'
            else:
                if (rs.recipe.hic_target >  0):
                    threshmet = int(value)/(rs.recipe.hic_target * rs.species.genome_size_update)
                    css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
                    if(threshmet > 0.25):
                        css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
                    if(threshmet > 0.5):
                        css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
                    if(threshmet > 0.75):
                        css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
                    if(threshmet >= 1.0):
                        css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        #cov = int(value)/rs.species.genome_size_update if int(value) else ""
        if (value == 0 or rs.recipe.hic_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_ena_hic_yield(self, value):
        if value:
            return value
        else:
            return 0

    def render_ena_short_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe):
            if(rs.recipe.short_target == 0):
                if(int(value)>0):
                    css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'
            else:
                if (rs.recipe.short_target >  0):
                    threshmet = int(value)/(rs.recipe.short_target * rs.species.genome_size_update)
                    css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
                    if(threshmet > 0.25):
                        css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
                    if(threshmet > 0.5):
                        css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
                    if(threshmet > 0.75):
                        css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
                    if(threshmet >= 1.0):
                        css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        #cov = int(value)/rs.species.genome_size_update if int(value) else ""
        if (value == 0 or rs.recipe.short_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_ena_short_yield(self, value):
        if value:
            return value
        else:
            return 0

    def render_ena_rnaseq_pe(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe and (rs.recipe.rna_target >  0)):
            threshmet = int(value/1000000)/(rs.recipe.rna_target)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        if (value == 0 or rs.recipe.rna_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000) + "</span>")

    def value_ena_rnaseq_pe(self, value):
        if value:
            return value
        else:
            return 0

    def render_ena_ont_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe):
            if(rs.recipe.ont_target == 0):
                if(int(value)>0):
                    css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'
            else:
                if (rs.recipe.ont_target >  0):
                    threshmet = int(value)/(rs.recipe.ont_target * rs.species.genome_size_update)
                    css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
                    if(threshmet > 0.25):
                        css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
                    if(threshmet > 0.5):
                        css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
                    if(threshmet > 0.75):
                        css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
                    if(threshmet >= 1.0):
                        css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        #cov = int(value)/rs.species.genome_size_update
        if (value == 0 or rs.recipe.ont_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) +"</span>")

    def value_ena_ont_yield(self, value):
        if value is not None:
            return value
        else:
            return 0
    
    class Meta:
        model = Reads
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ("ont_ena","hifi_ena","hic_ena","short_ena","rnaseq_ena",),
        fields = ('project', 'seq_center', 'study_accession', 'ena_ont_yield', 'ena_ont_cov','ena_hifi_yield', 'ena_hifi_cov','ena_short_yield','ena_short_cov','ena_hic_yield','ena_hic_cov','ena_rnaseq_pe','runs')

class ReadsTable(tables.Table):
    project = tables.LinkColumn('sequencing_list')
    seq_center = tables.Column(accessor='project__species__gt_rel__sequencing_team__name',verbose_name='Center')
    ont_yield = tables.Column(verbose_name="ONT (Gb)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ont_cov = tables.Column(verbose_name="ONT (x)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ont_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    hifi_yield = tables.Column(verbose_name="HiFi (Gb)")
    hifi_cov = tables.Column(verbose_name="HiFi (x)")
    hifi_ena = tables.Column(verbose_name="ENA")
    short_yield = tables.Column(verbose_name="Illumina (Gb)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    short_cov = tables.Column(verbose_name="Illumina (x)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    short_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    hic_yield = tables.Column(verbose_name="Hi-C (Gb)")
    hic_cov = tables.Column(verbose_name="Hi-C (x)")
    hic_ena = tables.Column(verbose_name="ENA")
    rnaseq_pe = tables.Column(verbose_name="RNA-seq (MPE)",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    rnaseq_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    runs = tables.TemplateColumn('<a href="{% url \'runs_list\' %}?project={{record.project.pk}}&sort=read_type">{{record.project}}</a>',empty_values=(), verbose_name='Runs')

    def render_ont_ena(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_hifi_ena(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_hic_ena(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_short_ena(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_rnaseq_ena(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/ena/browser/view/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_project(self, value, record):
        url = reverse('sequencing_list')
        return format_html('<a href="{}?project={}">{}</a>', url, record.project.pk, value)

    def value_project(self, value):
        return value

    def render_hifi_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.hifi_target >  0):
            threshmet = int(value)/(rs.recipe.hifi_target * rs.species.genome_size_update)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size_update
        if (value == 0 and rs.recipe.hifi_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_hifi_yield(self, value):
        return value

    def render_hic_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.hic_target >  0):
            threshmet = int(value)/(rs.recipe.hic_target * rs.species.genome_size_update)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size_update
        if (value == 0 and rs.recipe.hic_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_hic_yield(self, value):
        return value

    def render_short_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.short_target >  0):
            threshmet = int(value)/(rs.recipe.short_target * rs.species.genome_size_update)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size_update
        if (value == 0 and rs.recipe.short_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "</span>")

    def value_short_yield(self, value):
        return value

    def render_rnaseq_pe(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.rna_target >  0):
            threshmet = int(value)/(rs.recipe.rna_target)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        if (value == 0 and rs.recipe.rna_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000) + "</span>")

    def value_rnaseq_pe(self, value):
        return value

    def render_ont_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.ont_target >  0):
            threshmet = int(value)/(rs.recipe.ont_target * rs.species.genome_size_update)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size_update
        if (value == 0 and rs.recipe.ont_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) +"</span>")

    def value_ont_yield(self, value):
        return value
    
    class Meta:
        model = Reads
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('project', 'seq_center', 'ont_yield', 'ont_cov','ont_ena','hifi_yield', 'hifi_cov','hifi_ena','short_yield','short_cov','short_ena','hic_yield','hic_cov','hic_ena','rnaseq_pe','rnaseq_ena','runs')

class CurationTable(tables.Table):
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__genometeam__curation_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = Curation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class AnnotationTable(tables.Table):
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=(),verbose_name='Species')
    team = tables.Column(accessor='species__gt_rel__annotation_team',linkify=True, verbose_name='Team')

    def value_status(self, value):
        return value

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'status','ensembl','note')

class CommunityAnnotationTable(tables.Table):
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__gt_rel__community_annotation_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class SpecimenTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    samples = tables.TemplateColumn('<a href="{% url \'sample_list\' %}?specimen={{ record.pk|stringformat:"s" }}">samples</a>',empty_values=(), verbose_name='Samples', orderable=False)
    #from_manifest = tables.LinkColumn("from_manifest_detail", kwargs={"specimen_id": tables.A("specimen_id")}, empty_values=())
    #from_manifest = tables.Column(accessor='manifest_roles_rel',linkify=True)
    from_manifest = tables.LinkColumn("from_manifest_detail", kwargs={"specimen_id": tables.A("pk")}, text='contributors', empty_values=(), verbose_name='People', orderable=False)
    #from_manifest = tables.TemplateColumn('<a href="{% url \'from_manifest_detail\' %}?specimen_id={{record.specimen_id}}">roles from manifest</a>',empty_values=(), verbose_name='Manifest Roles')
    # coordinator = tables.ManyToManyColumn(verbose_name="Coordinator",transform=lambda obj: mark_safe('<a href="{}">{}</a>'.format(obj.get_absolute_url(), str(obj))))
    # collector = tables.ManyToManyColumn(verbose_name="Collector",transform=lambda obj: mark_safe('<a href="{}">{}</a>'.format(obj.get_absolute_url(), str(obj))))
    # identifier = tables.ManyToManyColumn(verbose_name="Identifier",transform=lambda obj: mark_safe('<a href="{}">{}</a>'.format(obj.get_absolute_url(), str(obj))))
    # preserver = tables.ManyToManyColumn(verbose_name="Preserver",transform=lambda obj: mark_safe('<a href="{}">{}</a>'.format(obj.get_absolute_url(), str(obj))))
    # nagoya_statement = tables.URLColumn()
    #collection = tables.Column(linkify=True)
    # def __init__(self, *args, **kwargs):
    #     self.columns['nagoya_statement'].column.attrs = {"td":{"style" : "width:200;" }}
    def render_biosampleAccession(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/biosamples/samples/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)
    def render_collection(self, value, record):
        html = '<a href="' + settings.DEFAULT_DOMAIN + 'collection/?species='+str(record.species.pk)+'">'+escape(value)+'</a>'
        return mark_safe(html)
    def render_nagoya_statement(self, value, record):
        return mark_safe("<div style='width:300'>"+value.statement+"</div>")
    class Meta:
        model = Specimen
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id','sample_coordinator']
        sequence = ('specimen_id','species','tolid','biosampleAccession','samples','...')

class SampleTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    # biosampleAccession = tables.TemplateColumn( '<a href="https://www.ebi.ac.uk/biosamples/samples/{{record.biosampleAccession}}"{{record.biosampleAccession}}</a>',empty_values=(), verbose_name='BioSample')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    def render_specimen(self, value, record):
        html = '<a target="blank" <a href="' + settings.DEFAULT_DOMAIN + 'specimens/'+ str(record.specimen.pk) +'/">'+escape(value)+'</a>'
        return mark_safe(html)

    #specimen = tables.Column(linkify=True)
    #copo = tables.TemplateColumn('<a href="{% url \'copo\' %}/{{record.copo_id}}/">copo</a>',empty_values=(), verbose_name='COPO Record')
    def render_copo_id(self, value, record):
        html = '<a target="blank" <a href="' + settings.DEFAULT_DOMAIN + 'copo/'+ value +'">'+escape(value)+'</a>'
        return mark_safe(html)

    def render_biosampleAccession(self, value, record):
        html = '<a target="blank" href="https://www.ebi.ac.uk/biosamples/samples/'+value+'">'+escape(value)+'</a>'
        return mark_safe(html)
    class Meta:
        model = Sample
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id','barcode']

class GenomeTeamsTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    sample_handling_team = tables.Column(verbose_name='Sample Handling',linkify=True)
    sample_coordinator = tables.Column(verbose_name='Sample Coordinator',linkify=True)
    coordinator = tables.Column(verbose_name='Coordinator',linkify=True)
    collection_team = tables.Column(verbose_name='Collection',linkify=True)
    taxonomy_team = tables.Column(verbose_name='Taxonomy',linkify=True)
    barcoding_team = tables.Column(verbose_name='Barcoding',linkify=True)
    vouchering_team = tables.Column(verbose_name='Vouchering',linkify=True)
    biobanking_team = tables.Column(verbose_name='Biobanking',linkify=True)
    sequencing_team = tables.Column(verbose_name='Sequencing',linkify=True)
    hic_team = tables.Column(verbose_name='Hi-C',linkify=True)
    assembly_team = tables.Column(verbose_name='Assembly',linkify=True)
    community_annotation_team = tables.Column(verbose_name='Community Annotation',linkify=True)
    annotation_team = tables.Column(verbose_name='Annotation',linkify=True)
    #extraction_team = tables.Column(verbose_name='Extraction',linkify=True)

    class Meta:
        model = GenomeTeam
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id','extraction_team']

class AuthorsTable(tables.Table):
    export_formats = ['csv', 'tsv', 'json']
    # def render_author(self, value, record):
    #     html = '<a target="blank" <a href="/erga-stream-dev/specimens/'+ str(record.specimen.pk) +'/">'+escape(value)+'</a>'
    #     return mark_safe(html)
    #team = tables.Column(accessor='author',linkify=True)
    name = tables.TemplateColumn("{{record.author.last_name}},{{record.author.first_name}}{%if record.author.middle_name %} {{record.author.middle_name}}{% endif %}",empty_values=(), verbose_name='Author')
    affiliation = tables.Column(accessor='author__affiliation')
    orcid = tables.Column(accessor='author__orcid')

    def render_affiliation(self, value, table):
        alist = ""
        afirst = True

        affs = list(value.all())

        for a in affs:
            if not afirst:
                alist += "<br />"
            else:
                afirst = False

            alist += a.affiliation

        return mark_safe(alist)
    
    class Meta:
        model = Author
        template_name = "django_tables2/bootstrap4.html"
        #order_by = 'taxon_kingdom,taxon_phylum,taxon_class,taxon_order,taxon_family,taxon_genus,scientific_name' # use dash for descending order
        paginate = {"per_page": 100}
        fields = ('species','role','name','affiliation','orcid')

class StatusUpdateTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    # status = tables.Column(accessor='samplecollection.genomic_sample_status',verbose_name='Genomic Sample',attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    attrs={"td": {"class": "overview-table"}}

    def render_status(self, value, record):
        html = '<span class="status '+escape(value)+'">'+escape(value)+'</span>'
        return mark_safe(html)
    
    class Meta:
        model = StatusUpdate
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'process','status','note','timestamp')
