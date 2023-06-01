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
#import html
class OverviewTable(tables.Table):
    export_formats = ['csv', 'tsv','xls']
    # collection_status = tables.LinkColumn("collection_list",  kwargs={"species": tables.A("pk")},accessor='samplecollection.status',verbose_name='Collection')
    # genomic_sample_status = tables.Column(accessor='samplecollection.genomic_sample_status',verbose_name='Genomic Sample',attrs={
    #     "td": {
    #         "background-color": "#e5e5f7",
    #         "opacity": "0.8",
    #         "background-size":"6px 6px","background-image":"repeating-linear-gradient(45deg, #c6c9fc 0, #c6c9fc 0.6000000000000001px, #e5e5f7 0, #e5e5f7 50%)"
    #         }
    #     }
    # )
    genomic_sample_status = tables.Column(accessor='samplecollection.genomic_sample_status',verbose_name='Samples',attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    # hic_sample_status = tables.Column(accessor='samplecollection.hic_sample_status',verbose_name='HiC Sample',attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    # rna_sample_status = tables.Column(accessor='samplecollection.rna_sample_status',verbose_name='RNA Sample',attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    long_seq_status = tables.Column(accessor='sequencing.long_seq_status',verbose_name='Long',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    short_seq_status = tables.Column(accessor='sequencing.short_seq_status',verbose_name='Short',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    hic_seq_status = tables.Column(accessor='sequencing.hic_seq_status',verbose_name='HiC',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    rna_seq_status = tables.Column(accessor='sequencing.rna_seq_status',verbose_name='RNA-Seq',attrs={"td": {"class": "seq_col"},"th": {"class": "seq_col"}})
    assembly_status = tables.Column(accessor='assemblyproject.status',verbose_name='Assembly',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    # curation_status = tables.Column(accessor='curation.status',verbose_name='Curation',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    community_annotation_status = tables.Column(accessor='communityannotation.status',verbose_name='Community Annotation',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    annotation_status = tables.Column(accessor='annotation.status',verbose_name='Annotation',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})
    # submission_status = tables.Column(accessor='submission.status',verbose_name='Submission',attrs={"td": {"class": "analysis_col"},"th": {"class": "analysis_col"}})

    tolid_prefix = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    scientific_name = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    # scientific_name = tables.Column(linkify=True)
    #listed_species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    #log = tables.Column(accessor='updatestatus',verbose_name='Log')
    log = tables.TemplateColumn('<a href="/erga-stream-dev/log/?species={{record.id}}"><i class="fas fa-history"></i></a>',empty_values=(), verbose_name='log')
    attrs={"td": {"class": "overview-table"}}
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
    def render_scientific_name(self, value, record):
        url = reverse('species_detail',kwargs={'pk': record.pk})
        if (str(value) == str(record.listed_species)):
            return format_html('<a href="{}">{}</a>',url, str(value))
        else:
            return format_html('<a href="{}">{}</a>',url, str(value) + " (" + str(record.listed_species) + ")") #'<a href="{}/{}">{}</a>', 
    def value_scientific_name(self, value):
        return value
      
    def render_genomic_sample_status(self, value, record):
        html = '<a href="/erga-stream-dev/collection/?species='+str(record.pk)+'"><span class="status '+escape(value.replace(" ",''))+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_genomic_sample_status(self, value):
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
        html = '<a href="/erga-stream-dev/sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_long_seq_status(self, value):
        return value

    def render_short_seq_status(self, value, record):
        html = '<a href="/erga-stream-dev/sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_short_seq_status(self, value):
        return value
    
    def render_hic_seq_status(self, value, record):
        html = '<a href="/erga-stream-dev/sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_hic_seq_status(self, value):
        return value

    def render_rna_seq_status(self, value, record):
        html = '<a href="/erga-stream-dev/sequencing/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_rna_seq_status(self, value):
        return value
    def render_assembly_status(self, value, record):
        html = '<a href="/erga-stream-dev/projects/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_assembly_status(self, value):
        return value

    # def render_curation_status(self, value, record):
    #     html = '<a href="/erga-stream-dev/curation/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
    #     return mark_safe(html)

    # def value_curation_status(self, value):
    #     return value

    def render_annotation_status(self, value, record):
        html = '<a href="/erga-stream-dev/annotation/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_annotation_status(self, value):
        return value
    
    def render_community_annotation_status(self, value, record):
        html = '<a href="/erga-stream-dev/community_annotation/?species='+str(record.pk)+'"><span class="status '+escape(value)+'">'+escape(value)+'</span></a>'
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
        fields = ('scientific_name','tolid_prefix','log','genomic_sample_status','genomic_seq_status','hic_seq_status','rna_seq_status','assembly_status','annotation_status','community_annotation_status')

class TargetSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    scientific_name = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("pk")}, empty_values=())
    #listed_species = tables.Column()
    def render_scientific_name(self, value, record):
        url = reverse('species_detail',kwargs={'pk': record.pk})
        if (str(value) == str(record.listed_species)):
            return format_html('<a href="{}">{}</a>',url, str(value))
        else:
            return format_html('<a href="{}">{}</a>',url, str(value) + " (" + str(record.listed_species) + ")")
    #tolid_prefix = tables.Column(linkify=True)
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        #order_by = 'taxon_kingdom,taxon_phylum,taxon_class,taxon_order,taxon_family,taxon_genus,scientific_name' # use dash for descending order
        paginate = {"per_page": 100}
        fields = ('scientific_name','tags','taxon_id', 'genome_size', 'c_value','ploidy','haploid_number','taxon_kingdom','taxon_phylum','taxon_class','taxon_order','taxon_family','taxon_genus')

class AssemblyTable(tables.Table):
    export_formats = ['csv', 'tsv']
    project = tables.LinkColumn('assembly_project_list')
    pipeline = tables.Column(linkify=True)
    span = tables.Column(verbose_name="Span (Gb)")
    contig_n50 = tables.Column(verbose_name="Contig N50 (Mb)")
    scaffold_n50 = tables.Column(verbose_name="Scaffold N50 (Mb)")
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
    class Meta:
        model = Assembly
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}

class AssemblyProjectTable(tables.Table):
    export_formats = ['csv', 'tsv']
    assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__genometeam__assembly_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = AssemblyProject
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team','assemblies', 'note', 'status')

class SampleCollectionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    genomic_sample_status = tables.TemplateColumn('<span class="status {{record.genomic_sample_status|cut:" "}}">{{record.genomic_sample_status}}</span>',empty_values=(), verbose_name='Genomic Sample')
    # hic_sample_status = tables.TemplateColumn('<span class="{{record.hic_sample_status}}">{{record.hic_sample_status}}</span>',empty_values=(), verbose_name='HiC Sample')
    rna_sample_status = tables.TemplateColumn('<span class="status {{record.rna_sample_status|cut:" "}}">{{record.rna_sample_status}}</span>',empty_values=(), verbose_name='RNA Sample')
    # species = tables.Column(linkify=True)
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    specimens = tables.TemplateColumn('<a href="{% url \'specimen_list\' %}?collection={{record.pk}}">specimens</a>',empty_values=(), verbose_name='Specimen(s)')
    team = tables.Column(accessor='species__genometeam__collection_team',linkify=True)

    def value_genomic_sample_status(self, value):
        return value
    # def value_hic_sample_status(self, value):
    #     return value
    def value_rna_sample_status(self, value):
        return value

    class Meta:
        model = SampleCollection
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        #fields = ('species', 'team', 'specimens','note', 'genomic_sample_status','hic_sample_status','rna_sample_status')
        fields = ('species', 'team', 'specimens','note', 'genomic_sample_status','rna_sample_status')

class SequencingTable(tables.Table):
    genomic_seq_status = tables.TemplateColumn('<span class="status {{record.genomic_seq_status}}">{{record.genomic_seq_status}}</span>',empty_values=(), verbose_name='gDNA Status')
    hic_seq_status = tables.TemplateColumn('<span class="status {{record.hic_seq_status}}">{{record.hic_seq_status}}</span>',empty_values=(), verbose_name='HiC Status')
    rna_seq_status = tables.TemplateColumn('<span class="status {{record.rna_seq_status}}">{{record.rna_seq_status}}</span>',empty_values=(), verbose_name='RNA Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__genometeam__sequencing_team',linkify=True)
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
        fields = ('species', 'team', 'recipe', 'note', 'reads', 'genomic_seq_status','hic_seq_status','rna_seq_status')

class ReadsTable(tables.Table):
    project = tables.LinkColumn('sequencing_list')
    ont_yield = tables.Column(verbose_name="ONT yield",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    ont_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    hifi_yield = tables.Column(verbose_name="HiFi yield")
    hifi_ena = tables.Column(verbose_name="ENA")
    short_yield = tables.Column(verbose_name="Short read yield",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    short_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    hic_yield = tables.Column(verbose_name="Hi-C yield")
    #sum_hic = tables.Column(verbose_name="HiC Sum")
    hic_ena = tables.Column(verbose_name="ENA")
    rnaseq_pe = tables.Column(verbose_name="RNA-seq yield",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
    rnaseq_ena = tables.Column(verbose_name="ENA",attrs={"td": {"class": "sample_col"},"th": {"class": "sample_col"}})
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
            threshmet = int(value)/(rs.recipe.hifi_target * rs.species.genome_size)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size
        if (value == 0 and rs.recipe.hifi_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + " Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def value_hifi_yield(self, value):
        return value
    
    # def render_sum_hic(self, value, record):
    #     rs = Sequencing.objects.get(pk=record.project.pk)
    #     threshmet = 1.0
    #     css_class = '<i class="fas fa-ban fa-lg"></i>'
    #     if (rs.recipe.hic_target >  0):
    #         threshmet = int(value)/(rs.recipe.hic_target * rs.species.genome_size)
    #         css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
    #         if(threshmet > 0.25):
    #             css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
    #         if(threshmet > 0.5):
    #             css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
    #         if(threshmet > 0.75):
    #             css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
    #         if(threshmet >= 1.0):
    #             css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

    #     cov = int(value)/rs.species.genome_size
    #     if (value == 0 and rs.recipe.hic_target == 0):
    #         return ''
    #     else:
    #         return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + " Gb (" + "{:.1f}".format(cov) + "x)</span>")

    # def value_hsum_hic(self, value):
    #     return value

    def render_hic_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.hic_target >  0):
            threshmet = int(value)/(rs.recipe.hic_target * rs.species.genome_size)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size
        if (value == 0 and rs.recipe.hic_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + " Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def value_hic_yield(self, value):
        return value

    def render_short_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.short_target >  0):
            threshmet = int(value)/(rs.recipe.short_target * rs.species.genome_size)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size
        if (value == 0 and rs.recipe.short_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + " Gb (" + "{:.1f}".format(cov) + "x)</span>")

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
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000) + " MPE</span>")

    def value_rnaseq_pe(self, value):
        return value

    def render_ont_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.recipe.ont_target >  0):
            threshmet = int(value)/(rs.recipe.ont_target * rs.species.genome_size)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        cov = int(value)/rs.species.genome_size
        if (value == 0 and rs.recipe.ont_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + " Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def value_ont_yield(self, value):
        return value

    class Meta:
        model = Reads
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('project', 'ont_yield', 'ont_ena','hifi_yield', 'hifi_ena','short_yield','short_ena','hic_yield','hic_ena','rnaseq_pe','rnaseq_ena')

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
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__genometeam__annotation_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class CommunityAnnotationTable(tables.Table):
    status = tables.TemplateColumn('<span class="status {{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    team = tables.Column(accessor='species__genometeam__community_annotation_team',linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

""" class SubmissionTable(tables.Table):
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</span>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    def value_status(self, value):
        return value

    class Meta:
        model = Submission
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status') """

class SpecimenTable(tables.Table):
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    samples = tables.TemplateColumn('<a href="{% url \'sample_list\' %}?specimen={{record.pk}}">samples</a>',empty_values=(), verbose_name='Samples')
    #nagoya_statement = tables.URLColumn()
    #collection = tables.Column(linkify=True)
    # def __init__(self, *args, **kwargs):
    #     self.columns['nagoya_statement'].column.attrs = {"td":{"style" : "width:200;" }}
    def render_collection(self, value, record):
        html = '<a href="/erga-stream-dev/collection/?species='+str(record.species.pk)+'">'+escape(value)+'</a>'
        return mark_safe(html)
    def render_nagoya_statement(self, value, record):
        return mark_safe("<div style='width:300'>"+value.statement+"</div>")
    class Meta:
        model = Specimen
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        exclude = ['id']

class SampleTable(tables.Table):
    # biosampleAccession = tables.TemplateColumn( '<a href="https://www.ebi.ac.uk/biosamples/samples/{{record.biosampleAccession}}"{{record.biosampleAccession}}</a>',empty_values=(), verbose_name='BioSample')
    species = tables.LinkColumn("species_detail", kwargs={"pk": tables.A("species.pk")}, empty_values=())
    def render_specimen(self, value, record):
        html = '<a target="blank" <a href="/erga-stream-dev/specimens/'+ str(record.specimen.pk) +'/">'+escape(value)+'</a>'
        return mark_safe(html)

    #specimen = tables.Column(linkify=True)
    #copo = tables.TemplateColumn('<a href="{% url \'copo\' %}/{{record.copo_id}}/">copo</a>',empty_values=(), verbose_name='COPO Record')
    def render_copo_id(self, value, record):
        html = '<a target="blank" <a href="/erga-stream-dev/copo/'+ value +'">'+escape(value)+'</a>'
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
    collection_team = tables.Column(verbose_name='Collection',linkify=True)
    taxonomy_team = tables.Column(verbose_name='Taxonomy',linkify=True)
    barcoding_team = tables.Column(verbose_name='Barcoding',linkify=True)
    vouchering_team = tables.Column(verbose_name='Vouchering',linkify=True)
    biobanking_team = tables.Column(verbose_name='Biobanking',linkify=True)
    sequencing_team = tables.Column(verbose_name='Sequencing',linkify=True)
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
