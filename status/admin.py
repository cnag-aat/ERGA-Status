from django.contrib import admin
from django.contrib.admin.decorators import register
from status.models import *
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.helpers import ActionForm
from django import forms
from django.contrib import messages
from django.forms.widgets import DateInput
from django.contrib.admin.widgets import AdminDateWidget
from dateutil.parser import parse
from status.widgets import CustomDatePickerWidget

class ExportCsvMixin:
    def export_as_csv(self, request, queryset):

        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected"

def export_csv(modeladmin, request, queryset):
    import csv
    from django.utils.encoding import smart_str
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=samples.csv'
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)
    #field_names = queryset.keys()
    for obj in queryset:
        row =[]
        for name in obj._meta.fields:
            try:
                row.append(str(getattr(property, name)))
            except:
                row.append(" ")
        writer.writerow(row)
    return response
export_csv.short_description = "Export CSV"

# Register your models here.
GOAT_TARGET_LIST_STATUS_CHOICES = (
    ('none', 'none'),
    ('long_list', 'long_list'),
    ('other_priority', 'other_priority'),
    ('family_representative', 'family_representative'),
    ('removed', 'removed')
)

GOAT_SEQUENCING_STATUS_CHOICES = (
    ('none', 'none'),
    ('sample_collected', 'sample_collected'),
    ('sample_acquired', 'sample_acquired'),
    ('data_generation', 'data_generation'),
    ('in_assembly', 'in_assembly'),
    ('insdc_open', 'insdc_open'),
    ('publication_available', 'publication_available')
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

class UpdateSpeciesActionForm(ActionForm):
    # tags = forms.ModelMultipleChoiceField(
    #     queryset=Tag.objects.all().order_by('tag'),
    #     required=False
    # )
    goat_target_list_status = forms.ChoiceField(
        choices = GOAT_TARGET_LIST_STATUS_CHOICES,
        required=False
    )

    goat_sequencing_status = forms.ChoiceField(
        choices = GOAT_SEQUENCING_STATUS_CHOICES,
        required=False
    )

# def add_tags(modeladmin, request, queryset):
#     if 'tags' in request.POST:
#         tags = request.POST.getlist('tags')
#         try:
#             for obj in queryset:
#                 for t in tags:
#                     obj.tags.add(t)
#         except ValueError:
#              pass
#     messages.add_message(request, messages.INFO, "Added tags successfully")

# def remove_tags(modeladmin, request, queryset):
#     if 'tags' in request.POST:
#         tags = request.POST.getlist('tags')
#         try:
#             for obj in queryset:
#                 for t in tags:
#                     obj.tags.remove(t)
#         except ValueError:
#              pass
#     messages.add_message(request, messages.INFO, "Removed tags successfully")

def update_goat_list_status(modeladmin, request, queryset):
    if 'goat_target_list_status' in request.POST:
        goat_target_list_status = request.POST['goat_target_list_status']
        queryset.update(goat_target_list_status=goat_target_list_status)

def update_goat_seq_status(modeladmin, request, queryset):
    if 'goat_sequencing_status' in request.POST:
        goat_sequencing_status = request.POST['goat_sequencing_status']
        queryset.update(goat_sequencing_status=goat_sequencing_status)
    messages.add_message(request, messages.INFO, "GoaT status updated successfully")

class SampleCollectionInlineAdmin(admin.TabularInline):
    model = SampleCollection

class SubSpeciesInlineAdmin(admin.TabularInline):
    model = SubSpecies

@register(TargetSpecies)
class TargetSpeciesAdmin(admin.ModelAdmin):
    list_filter = ["gt_rel__sequencing_team","sequencing_rel__phase","collection_rel__country","collection_rel__task",'goat_target_list_status','goat_sequencing_status']
    #list_filter = ["sequencing_rel__phase","collection_rel__country","collection_rel__task","tags",'goat_target_list_status','goat_sequencing_status']
    action_form = UpdateSpeciesActionForm
    actions = [update_goat_list_status,update_goat_seq_status]
    # actions = [add_tags,remove_tags,update_goat_list_status,update_goat_seq_status]
    # inlines = [SampleCollectionInlineAdmin]
    inlines = [SubSpeciesInlineAdmin]
    def get_actions(self, request):
        actions = super(TargetSpeciesAdmin, self).get_actions(request)
        # try:
        #     del actions['delete_selected']
        # except KeyError:
        #     pass
        return actions
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            # 'show_delete': False, # Here
            # 'show_save': False,
            # 'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)
    list_per_page = 10000
    list_display = (
        'listed_species',
        'scientific_name',
        'tolid_prefix',
        # 'subspecies',
        # 'synonym',
        'taxon_id',
        'goat_target_list_status',
        'goat_sequencing_status',
        'ranking',
        # 'publication_id',
        # 'get_tags',
        # 'taxon_kingdom',
        'taxon_phylum',
        # 'taxon_class',
        # 'taxon_order',
        'taxon_family',
        # 'chromosome_number',
        'haploid_number',
        # 'ploidy',
        # 'c_value',
        'genome_size',
        'genome_size_update',
        'date_updated'
    )
    search_fields = ['scientific_name']
    readonly_fields=(
        'scientific_name',
        # 'tolid_prefix',
        # 'subspecies',
        # 'synonym',
        # 'taxon_id',
        # 'goat_target_list_status',
        # 'goat_sequencing_status',
        # 'publication_id',
        # 'get_tags',
        'taxon_kingdom',
        'taxon_phylum',
        'taxon_class',
        'taxon_order',
        'taxon_family',
        'taxon_genus',
        'chromosome_number',
        'haploid_number',
        'ploidy',
        'c_value',
        'genome_size',
        'gss_rank',
        'date_updated'
    )

admin.site.register(SubSpecies)

@register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    ordering = ('-modified', )
    list_display = (
        'user',
        'created',
        'modified',
        'first_name',
        'last_name',
        'lead',
        'get_roles',
        'get_affiliations'
    )
    search_fields = ['user__username','first_name','last_name']

class MyUserAdmin(UserAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return ' '.join(groups)
    group.short_description = 'Groups'
    # override the default sort column
    ordering = ('-date_joined', )
    list_filter = UserAdmin.list_filter + ('groups__name',)
    list_display = ('username', 'email', 'date_joined', 'first_name', 'last_name', 'is_staff', 'group')

@register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ['author__first_name','author__last_name','species__scientific_name']
    list_display = (
        'author',
        'species',
        'role'
    )

class StatementMultipleModelChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return "%s" % (obj.name)
    
class SpecimenUpdateActionForm(ActionForm):
    nagoya_statement = StatementMultipleModelChoiceField(
        queryset=Statement.objects.all().order_by('name'),
        required=False
    )

class UpdateActionForm(ActionForm):
    sample_handling_team = forms.ModelMultipleChoiceField(
        queryset=SampleHandlingTeam.objects.all().order_by('name'),
        required=False
    )
    sample_coordinator = forms.ModelMultipleChoiceField(
        queryset=UserProfile.objects.all().order_by('last_name'),
        required=False
    )
    collection_team = forms.ModelMultipleChoiceField(
        queryset=CollectionTeam.objects.all().order_by('name'),
        required=False
    )
    taxonomy_team = forms.ModelMultipleChoiceField(
        queryset=TaxonomyTeam.objects.all().order_by('name'),
        required=False
    )
    vouchering_team = forms.ModelMultipleChoiceField(
        queryset=VoucheringTeam.objects.all().order_by('name'),
        required=False
    )
    barcoding_team = forms.ModelMultipleChoiceField(
        queryset=BarcodingTeam.objects.all().order_by('name'),
        required=False
    )
    biobanking_team = forms.ModelMultipleChoiceField(
        queryset=BiobankingTeam.objects.all().order_by('name'),
        required=False
    )
    extraction_team = forms.ModelMultipleChoiceField(
        queryset=ExtractionTeam.objects.all().order_by('name'),
        required=False
    )
    sequencing_team = forms.ModelMultipleChoiceField(
        queryset=SequencingTeam.objects.all().order_by('name'),
        required=False
    )
    hic_team = forms.ModelMultipleChoiceField(
        queryset=HiCTeam.objects.all().order_by('name'),
        required=False
    )
    assembly_team = forms.ModelMultipleChoiceField(
        queryset=AssemblyTeam.objects.all().order_by('name'),
        required=False
    )
    community_annotation_team = forms.ModelMultipleChoiceField(
        queryset=CommunityAnnotationTeam.objects.all().order_by('name'),
        required=False
    )
    annotation_team = forms.ModelMultipleChoiceField(
        queryset=AnnotationTeam.objects.all().order_by('name'),
        required=False
    )

def update_teams(modeladmin, request, queryset):
    if 'sample_handling_team' in request.POST:
        sample_handling_team = request.POST['sample_handling_team']
        queryset.update(sample_handling_team=sample_handling_team)
    if 'sample_coordinator' in request.POST:
        sample_coordinator = request.POST['sample_coordinator']
        queryset.update(sample_coordinator=sample_coordinator)
    if 'collection_team' in request.POST:
        collection_team = request.POST['collection_team']
        queryset.update(collection_team=collection_team)
    if 'taxonomy_team' in request.POST:
        taxonomy_team = request.POST['taxonomy_team']
        queryset.update(taxonomy_team=taxonomy_team)
    if 'vouchering_team' in request.POST:
        vouchering_team = request.POST['vouchering_team']
        queryset.update(vouchering_team=vouchering_team)
    if 'barcoding_team' in request.POST:
        barcoding_team = request.POST['barcoding_team']
        queryset.update(barcoding_team=barcoding_team)
    if 'biobanking_team' in request.POST:
        biobanking_team = request.POST['biobanking_team']
        queryset.update(biobanking_team=biobanking_team)
    if 'extraction_team' in request.POST:
        extraction_team = request.POST['extraction_team']
        queryset.update(extraction_team=extraction_team)
    if 'sequencing_team' in request.POST:
        sequencing_team = request.POST['sequencing_team']
        queryset.update(sequencing_team=sequencing_team)
    if 'hic_team' in request.POST:
        hic_team = request.POST['hic_team']
        queryset.update(hic_team=hic_team)
    if 'assembly_team' in request.POST:
        assembly_team = request.POST['assembly_team']
        queryset.update(assembly_team=assembly_team)
    if 'community_annotation_team' in request.POST:
        community_annotation_team = request.POST['community_annotation_team']
        queryset.update(community_annotation_team=community_annotation_team)
    if 'annotation_team' in request.POST:
        annotation_team = request.POST['annotation_team']
        queryset.update(annotation_team=annotation_team)
    messages.add_message(request, messages.INFO, 'Successfully updated teams.')

@register(GenomeTeam)
class GenomeTeamAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = admin.ModelAdmin.list_filter + ('sample_handling_team','sequencing_team','hic_team','assembly_team','species__collection_rel__task','species__sequencing_rel__phase','species__goat_target_list_status')
    list_per_page = 10000
    list_display = (
        'species',
        'sample_handling_team',
        'sequencing_team',
        'hic_team',
        'assembly_team',
        'community_annotation_team'
    )
    readonly_fields=(
        'species',
    )
    search_fields = ['species__scientific_name']
    action_form = UpdateActionForm
    actions = [update_teams]
    def get_actions(self, request):
      actions = super(GenomeTeamAdmin, self).get_actions(request)
      try:
          del actions['delete_selected']
      except KeyError:
        pass
      return actions
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_delete': False, # Here
            # 'show_save': False,
            # 'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)
    def get_queryset(self, request):
        qs = super(GenomeTeamAdmin, self).get_queryset(request)
        return qs.exclude(species__goat_target_list_status = 'removed')
    
def update_specimens(modeladmin, request, queryset):
    if 'nagoya_statement' in request.POST:
        nagoya_statement = request.POST['nagoya_statement']
        queryset.update(nagoya_statement=nagoya_statement)
    messages.add_message(request, messages.INFO, 'Successfully updated specimen(s).')

@register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = admin.ModelAdmin.list_filter #+ ('species__tags',)
    search_fields = ['species__scientific_name']
    action_form = SpecimenUpdateActionForm
    actions = [update_specimens]
    def get_actions(self, request):
      actions = super(SpecimenAdmin, self).get_actions(request)
    #   try:
    #       del actions['delete_selected']
    #   except KeyError:
    #     pass
      return actions
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_delete': False, # Here
            # 'show_save': False,
            # 'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

admin.site.register(CommonNames)
admin.site.register(Synonyms)
admin.site.register(AnnotationTeam)
admin.site.register(CommunityAnnotationTeam)
admin.site.register(AssemblyTeam)
admin.site.register(Statement)
@register(AssemblyProject)
class AssemblyProjectAdmin(admin.ModelAdmin):
    list_filter = ["species__gt_rel__assembly_team"]
    list_display = (
        'species',
        'status',
        'note'
    )
    readonly_fields=(
        'species',
    )
    search_fields = ['species__scientific_name']
    def get_queryset(self, request):
        qs = super(AssemblyProjectAdmin, self).get_queryset(request)
        return qs.exclude(species__goat_target_list_status = 'removed')
    
@register(Assembly)
class AssemblyAdmin(admin.ModelAdmin):
    list_filter = ["project__species__gt_rel__sequencing_team","project__species__collection_rel__country","project__species__collection_rel__task"]
    #list_filter = ["species__gt_rel__sequencing_team","species__gt_rel__hic_team","species__tags","species__sequencing_rel__phase","species__collection_rel__country","species__collection_rel__task"]
    list_display = (
        'project',
        'description',
        'pipeline',
        'type',
        'contig_n50',
        'scaffold_n50',
        'qv'
    )

    # readonly_fields=(
    #     'project',
    # )
    search_fields = ['project__species__scientific_name']
admin.site.register(CollectionTeam)
admin.site.register(Subproject)
admin.site.register(Task)
admin.site.register(Country)
@register(SampleCollection)
class SampleCollectionAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ['species__scientific_name']
    list_filter = ["task",'subproject',"country__name","species__goat_sequencing_status","species__gt_rel__sample_handling_team","species__gt_rel__sequencing_team","sampling_delay"]
    list_display = ('species','task','country','copo_status','sample_provider_name','sample_provider_email','mta1','mta2','barcoding_status','sampling_delay','deadline_manifest_acceptance','note')
    actions = ["export_as_csv"]
    # formfield_overrides = {
    #     models.DateField: {'widget': CustomDatePickerWidget}
    # }
    
admin.site.register(CurationTeam)
admin.site.register(Curation)
admin.site.register(SequencingTeam)
admin.site.register(HiCTeam)
admin.site.register(VoucheringTeam)
admin.site.register(BarcodingTeam)
admin.site.register(TaxonomyTeam)
admin.site.register(SampleHandlingTeam)
admin.site.register(BiobankingTeam)
admin.site.register(ExtractionTeam)
admin.site.register(FromManifest)
admin.site.register(Phase)


class UpdateSequencingActionForm(ActionForm):
    phase = forms.ModelMultipleChoiceField(
        queryset=Phase.objects.all().order_by('name'),
        required=False
    )
    long_seq_status = forms.ChoiceField(
        choices = SEQUENCING_STATUS_CHOICES,
        required=False
    )
    short_seq_status = forms.ChoiceField(
        choices = SEQUENCING_STATUS_CHOICES,
        required=False
    )
    hic_seq_status = forms.ChoiceField(
        choices = SEQUENCING_STATUS_CHOICES,
        required=False
    )
    rna_seq_status = forms.ChoiceField(
        choices = SEQUENCING_STATUS_CHOICES,
        required=False
    )
    recipe = forms.ModelMultipleChoiceField(
        queryset=Recipe.objects.all().order_by('name'),
        required=False
    )

def update_sequencing(modeladmin, request, queryset):
    if 'phase' in request.POST:
        phase = request.POST['phase']
        queryset.update(phase=phase)
    if 'long_seq_status' in request.POST:
        long_seq_status = request.POST['long_seq_status']
        queryset.update(long_seq_status=long_seq_status)
    if 'short_seq_status' in request.POST:
        short_seq_status = request.POST['short_seq_status']
        queryset.update(short_seq_status=short_seq_status)
    if 'hic_seq_status' in request.POST:
        hic_seq_status = request.POST['hic_seq_status']
        queryset.update(hic_seq_status=hic_seq_status)
    if 'rna_seq_status' in request.POST:
        rna_seq_status = request.POST['rna_seq_status']
        queryset.update(rna_seq_status=rna_seq_status)
    if 'barcoding_team' in request.POST:
        barcoding_team = request.POST['barcoding_team']
        queryset.update(barcoding_team=barcoding_team)
    if 'recipe' in request.POST:
        recipe = request.POST['recipe']
        rec = Recipe.objects.get(pk=recipe)
        queryset.update(recipe=rec.name)
    messages.add_message(request, messages.INFO, 'Successfully updated sequencing. ' + recipe)


@register(Sequencing)
class SequencingAdmin(admin.ModelAdmin):
    list_filter = ["species__gt_rel__sequencing_team","species__gt_rel__hic_team","species__sequencing_rel__phase","species__collection_rel__country","species__collection_rel__task"]
    #list_filter = ["species__gt_rel__sequencing_team","species__gt_rel__hic_team","species__tags","species__sequencing_rel__phase","species__collection_rel__country","species__collection_rel__task"]
    list_display = (
        'species',
        'phase',
        'long_seq_status',
        'short_seq_status',
        'hic_seq_status',
        'rna_seq_status',
        'recipe',
        'note'
    )
    readonly_fields=(
        'species',
    )
    search_fields = ['species__scientific_name']
    # def queryset(self, request):
    #     qs = super(SequencingAdmin, self).queryset(request)
    #     seqteam_qs = SequencingTeam.objects.get(species=self.species)
    #     seqteam_qs.members
    #     if request.user.is_superuser:
    #         return qs
    #     else:
    #         return qs.filter(species__gt_rel__sequencing_team = seqteam)
    action_form = UpdateSequencingActionForm
    actions = [update_sequencing]
    def get_actions(self, request):
      actions = super(SequencingAdmin, self).get_actions(request)
      try:
          del actions['delete_selected']
      except KeyError:
        pass
      return actions
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_delete': False, # Here
            # 'show_save': False,
            # 'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)
    def get_queryset(self, request):
        qs = super(SequencingAdmin, self).get_queryset(request)
        return qs.exclude(species__goat_target_list_status = 'removed')
    
#admin.site.register(Reads)

@register(Reads)
class ReadsAdmin(admin.ModelAdmin, ExportCsvMixin):
    search_fields = ['project__species__scientific_name','ont_ena','hic_ena','hifi_ena','short_ena','rnaseq_ena','study_accession']
    #list_filter = ["task__name","country__name","species__goat_sequencing_status","species__gt_rel__sample_handling_team","species__gt_rel__sequencing_team","sampling_delay"]
    list_filter = ["project__species__gt_rel__sequencing_team"]
    list_display = ('project','ont_ena','hifi_ena','hic_ena','short_ena','rnaseq_ena','study_accession')
    actions = ["export_as_csv"]
    # ont_ena = models.CharField(max_length=12, null=True, blank=True, verbose_name="ONT Accession")
    # hifi_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="HiFi Accession")
    # hic_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Hi-C Accession")
    # short_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="Short read Accession")
    # rnaseq_ena = models.CharField(max_length=12,null=True, blank=True, verbose_name="RNAseq Accession")
    # study_accession = models.CharField(max_length=12, null=True, blank=True, verbose_name="Study")
    

@register(CommunityAnnotation)
class CommunityAnnotationAdmin(admin.ModelAdmin):
    search_fields = ['species__scientific_name']
    list_filter = ["species__gt_rel__community_annotation_team","species", "status"]
    list_display = (
        'species',
        'status',
        'note'
    )
    def get_queryset(self, request):
        qs = super(CommunityAnnotationAdmin, self).get_queryset(request)
        return qs.exclude(species__goat_target_list_status = 'removed')
    
@register(Annotation)
class AnnotationAdmin(admin.ModelAdmin):
    search_fields = ['species__scientific_name']
    list_filter = ["species__gt_rel__annotation_team","species", "status"]
    list_display = (
        'species',
        'status',
        'ensembl',
        'note'
    )
    readonly_fields=(
        'species',
    )
    def get_queryset(self, request):
        qs = super(AnnotationAdmin, self).get_queryset(request)
        return qs.exclude(species__goat_target_list_status = 'removed')

admin.site.register(BUSCOdb)
admin.site.register(BUSCOversion)
#admin.site.register(EnaRun)
@register(EnaRun)
class EnaRunAdmin(admin.ModelAdmin):
    list_filter = ["project__species__gt_rel__sequencing_team","project", "read_type"]
    list_display = (
        'project',
        'read_type',
        'seq_yield',
        'num_reads',
        'biosample_accession',
        'run_accession',
        'experiment_accession',
        'study_accession'
    )
    readonly_fields=(
        'project',
        'read_type',
        'seq_yield',
        'num_reads',
        'biosample_accession',
        'run_accession',
        'experiment_accession',
        'study_accession',
        'reads'
    )

@register(Run)
class RunAdmin(admin.ModelAdmin):
    list_filter = ["project__species__gt_rel__sequencing_team","project", "read_type"]
    list_display = (
        'project',
        'read_type',
        'seq_yield',
        'tube_or_well_id',
        'forward_filename',
        'forward_md5sum'
    )
    readonly_fields=(
        'project',
    )

LEFTOVER_CHOICES = (
    ('None', 'None'),
    ('DNA', 'DNA'),
    ('Tissue', 'Tissue'),
    ('Both', 'Both')
) 

ADMIN_LEFTOVER_CHOICES = (
    ('', '--------------'),
    ('None', 'None'),
    ('DNA', 'DNA'),
    ('Tissue', 'Tissue'),
    ('Both', 'Both')
) 

class UpdateSampleActionForm(ActionForm):
    date_sent = forms.DateField(widget=AdminDateWidget(),
        required=False)
    date_received = forms.DateField(widget=AdminDateWidget(),
        required=False)
    leftover = forms.ChoiceField(choices=ADMIN_LEFTOVER_CHOICES, required=False)

def update_samples(modeladmin, request, queryset):
    if 'date_sent' in request.POST:
        date_sent = request.POST['date_sent']
        try:
            parse(date_sent)
            queryset.update(date_sent=date_sent)
        except ValueError:
            pass
    if 'date_received' in request.POST:
        date_received = request.POST['date_received']
        try:
            parse(date_received)
            queryset.update(date_received=date_received)
        except ValueError:
            pass
    if 'leftover' in request.POST:
        leftover = request.POST['leftover']
        if (len(leftover) > 0):
            queryset.update(leftover=leftover)
    messages.add_message(request, messages.INFO, 'Successfully updated samples.')

@register(Sample)
class SampleAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = admin.ModelAdmin.list_filter + ('gal','specimen__sample_coordinator')
    action_form = UpdateSampleActionForm
    actions = [update_samples]
    def get_actions(self, request):
        actions = super(SampleAdmin, self).get_actions(request)
        # try:
        #     del actions['delete_selected']
        # except KeyError:
        #     pass
        return actions
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context.update({
            'show_delete': False, # Here
            # 'show_save': False,
            # 'show_save_and_continue': False,
        })
        return super().render_change_form(request, context, add, change, form_url, obj)

    list_display = (
        'tube_or_well_id',
        'biosampleAccession',
        'collector_sample_id',
        'specimen',
        'species',
        'gal',
        'leftover',
        'date_sent',
        'date_received'
    )
    readonly_fields=(
        'specimen',
    )
    search_fields = ['species__scientific_name']
admin.site.register(AssemblyPipeline)
admin.site.register(Person)
admin.site.register(Affiliation)
admin.site.register(Role)
# admin.site.register(Tag)
admin.site.register(Recipe)
@register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = (
        'species',
        'process',
        'status',
        'note',
        'timestamp'
    )
admin.site.unregister(User)
admin.site.register(User, MyUserAdmin)
