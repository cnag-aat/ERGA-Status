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
    genomic_sample_status = tables.Column(accessor='samplecollection.genomic_sample_status',verbose_name='Genomic Sample')
    hic_sample_status = tables.Column(accessor='samplecollection.hic_sample_status',verbose_name='HiC Sample')
    rna_sample_status = tables.Column(accessor='samplecollection.rna_sample_status',verbose_name='RNA Sample')
    genomic_seq_status = tables.Column(accessor='sequencing.genomic_seq_status',verbose_name='gDNA-Seq')
    hic_seq_status = tables.Column(accessor='sequencing.hic_seq_status',verbose_name='HiC-Seq')
    rna_seq_status = tables.Column(accessor='sequencing.rna_seq_status',verbose_name='RNA-Seq')
    assembly_status = tables.Column(accessor='assemblyproject.status',verbose_name='Assembly')
    curation_status = tables.Column(accessor='curation.status',verbose_name='Curation')
    annotation_status = tables.Column(accessor='annotation.status',verbose_name='Annotation')
    submission_status = tables.Column(accessor='submission.status',verbose_name='Submission')

    tolid_prefix = tables.Column(linkify=True)
    scientific_name = tables.Column(linkify=True)
    attrs={"td": {"class": "overview-table"}}
    #targetspecies=TargetSpecies.objects.get(=pk)
    # def render_collection_status(self, value):
    #     return mark_safe('<a href="'+
    #         url('collection_list',kwargs={'scientific_name': record.scientific_name})
    #         +'"><span class="'+escape(value)+'">'+escape(value)+'</span>')

    def render_genomic_sample_status(self, value, record):
        html = '<a href="/erga-status/collection/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_genomic_sample_status(self, value):
        return value

    def render_hic_sample_status(self, value, record):
        html = '<a href="/erga-status/collection/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_hic_sample_status(self, value):
        return value

    def render_rna_sample_status(self, value, record):
        html = '<a href="/erga-status/collection/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_rna_sample_status(self, value):
        return value

    def render_genomic_seq_status(self, value, record):
        html = '<a href="/erga-status/sequencing/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_genomic_seq_status(self, value):
        return value

    def render_hic_seq_status(self, value, record):
        html = '<a href="/erga-status/sequencing/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_hic_seq_status(self, value):
        return value

    def render_rna_seq_status(self, value, record):
        html = '<a href="/erga-status/sequencing/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_rna_seq_status(self, value):
        return value

    def render_assembly_status(self, value, record):
        html = '<a href="/erga-status/projects/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_assembly_status(self, value):
        return value

    def render_curation_status(self, value, record):
        html = '<a href="/erga-status/curation/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_curation_status(self, value):
        return value

    def render_annotation_status(self, value, record):
        html = '<a href="/erga-status/annotation/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_annotation_status(self, value):
        return value

    def render_submission_status(self, value, record):
        html = '<a href="/erga-status/submission/?species='+str(record.pk)+'"><span class="'+escape(value)+'">'+escape(value)+'</span></a>'
        return mark_safe(html)

    def value_submission_status(self, value):
        return value

    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('tolid_prefix', 'scientific_name','genomic_sample_status','hic_sample_status','rna_sample_status','genomic_seq_status','hic_seq_status','rna_seq_status','assembly_status','curation_status','annotation_status','submission_status')

class TargetSpeciesTable(tables.Table):
    export_formats = ['csv', 'tsv']
    scientific_name = tables.Column(linkify=True)
    tolid_prefix = tables.Column(linkify=True)
    class Meta:
        model = TargetSpecies
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('tolid_prefix', 'scientific_name','taxon_id', 'genome_size', 'c_value','ploidy','chromosome_number','haploid_number','taxon_kingdom','taxon_phylum','taxon_class','taxon','taxon_family','taxon_genus')

class AssemblyTable(tables.Table):
    export_formats = ['csv', 'tsv']
    project = tables.Column(linkify=True)
    span = tables.Column(verbose_name="Span (Gb)")
    contig_n50 = tables.Column(verbose_name="Contig N50 (Mb)")
    scaffold_n50 = tables.Column(verbose_name="Scaffold N50 (Mb)")
    def render_scaffold_n50(self, value, record):
        return "{:.3f}".format(record.scaffold_n50/1000000)
    def render_contig_n50(self, value, record):
        return "{:.3f}".format(record.contig_n50/1000000)
    def render_span(self, value, record):
        return "{:.3f}".format(record.span/1000000000)

    class Meta:
        model = Assembly
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}

class AssemblyProjectTable(tables.Table):
    export_formats = ['csv', 'tsv']
    assemblies = tables.TemplateColumn('<a href="{% url \'assembly_list\' %}?project={{record.pk}}">assemblies</a>',empty_values=(), verbose_name='Assemblies')
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = AssemblyProject
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team','assemblies', 'note', 'status')

class SampleCollectionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    genomic_sample_status = tables.TemplateColumn('<span class="{{record.genomic_sample_status}}">{{record.genomic_sample_status}}</a>',empty_values=(), verbose_name='Genomic Sample')
    hic_sample_status = tables.TemplateColumn('<span class="{{record.hic_sample_status}}">{{record.hic_sample_status}}</a>',empty_values=(), verbose_name='HiC Sample')
    rna_sample_status = tables.TemplateColumn('<span class="{{record.rna_sample_status}}">{{record.rna_sample_status}}</a>',empty_values=(), verbose_name='RNA Sample')
    species = tables.Column(linkify=True)
    specimens = tables.TemplateColumn('<a href="{% url \'specimen_list\' %}?collection={{record.pk}}">specimens</a>',empty_values=(), verbose_name='Specimen(s)')
    team = tables.Column(linkify=True)

    class Meta:
        model = SampleCollection
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'specimens','note', 'genomic_sample_status','hic_sample_status','rna_sample_status')

class SequencingTable(tables.Table):
    export_formats = ['csv', 'tsv']
    genomic_seq_status = tables.TemplateColumn('<span class="{{record.genomic_seq_status}}">{{record.genomic_seq_status}}</a>',empty_values=(), verbose_name='gDNA Status')
    hic_seq_status = tables.TemplateColumn('<span class="{{record.hic_seq_status}}">{{record.hic_seq_status}}</a>',empty_values=(), verbose_name='HiC Status')
    rna_seq_status = tables.TemplateColumn('<span class="{{record.rna_seq_status}}">{{record.rna_seq_status}}</a>',empty_values=(), verbose_name='RNA Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)
    reads = tables.TemplateColumn('<a href="{% url \'reads_list\' %}?project={{record.pk}}">reads</a>',empty_values=(), verbose_name='Reads')

    class Meta:
        model = Sequencing
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('id','species', 'team', 'note', 'reads', 'genomic_seq_status','hic_seq_status','rna_seq_status')

class ReadsTable(tables.Table):
    export_formats = ['csv', 'tsv']
    project = tables.LinkColumn('sequencing_list')
    ont_yield = tables.Column(verbose_name="ONT yield")
    hifi_yield = tables.Column(verbose_name="HiFi yield")
    hic_yield = tables.Column(verbose_name="Hi-C yield")
    short_yield = tables.Column(verbose_name="Short read yield")
    rnaseq_numlibs = tables.Column(verbose_name="RNAseq libs")

    def render_project(self, value, record):
        url = reverse('sequencing_list')
        return format_html('<a href="{}?project={}">{}</a>', url, record.project.pk, value)

    def render_hifi_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.hifi_target >  0):
            threshmet = int(value)/(rs.hifi_target * rs.species.genome_size)
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
        if (value == 0 and rs.hifi_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def render_hic_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.hic_target >  0):
            threshmet = int(value)/(rs.hic_target * rs.species.genome_size)
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
        if (value == 0 and rs.hic_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def render_short_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.short_target >  0):
            threshmet = int(value)/(rs.short_target * rs.species.genome_size)
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
        if (value == 0 and rs.short_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "Gb (" + "{:.1f}".format(cov) + "x)</span>")

    def render_rnaseq_numlibs(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.rnaseq_numlibs_target >  0):
            threshmet = int(value)/(rs.rnaseq_numlibs_target)
            css_class = '<i class="fas fa-battery-empty fa-lg empty-color"></i>'
            if(threshmet > 0.25):
                css_class = '<i class="fas fa-battery-quarter fa-lg quarter-color"></i>'
            if(threshmet > 0.5):
                css_class = '<i class="fas fa-battery-half fa-lg half-color"></i>'
            if(threshmet > 0.75):
                css_class = '<i class="fas fa-battery-three-quarters fa-lg threequarters-color"></i>'
            if(threshmet >= 1.0):
                css_class = '<i class="fas fa-battery-full fa-lg full-color"></i>'

        if (value == 0 and rs.rnaseq_numlibs_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;" + str(value) + "</span>")

    def render_ont_yield(self, value, record):
        rs = Sequencing.objects.get(pk=record.project.pk)
        threshmet = 1.0
        css_class = '<i class="fas fa-ban fa-lg"></i>'
        if (rs.ont_target >  0):
            threshmet = int(value)/(rs.ont_target * rs.species.genome_size)
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
        if (value == 0 and rs.ont_target == 0):
            return ''
        else:
            return mark_safe(css_class + "<span>&nbsp;{:.1f}".format(value/1000000000) + "Gb (" + "{:.1f}".format(cov) + "x)</span>")

    class Meta:
        model = Reads
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('project', 'ont_yield', 'hifi_yield', 'short_yield','hic_yield','rnaseq_numlibs')

class CurationTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Curation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class AnnotationTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Annotation
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class SubmissionTable(tables.Table):
    export_formats = ['csv', 'tsv']
    status = tables.TemplateColumn('<span class="{{record.status}}">{{record.status}}</a>',empty_values=(), verbose_name='Status')
    species = tables.Column(linkify=True)
    team = tables.Column(linkify=True)

    class Meta:
        model = Submission
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
        fields = ('species', 'team', 'note', 'status')

class SpecimenTable(tables.Table):
    export_formats = ['csv', 'tsv']

    class Meta:
        model = Specimen
        template_name = "django_tables2/bootstrap4.html"
        paginate = {"per_page": 100}
