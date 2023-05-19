from django.contrib import admin
from django.contrib.admin.decorators import register
from status.models import *
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.helpers import ActionForm
from django import forms
from django.contrib import messages

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
@register(TargetSpecies)
class TargetSpeciesAdmin(admin.ModelAdmin):
    list_display = (
        'scientific_name',
        'tolid_prefix',
        'get_tags',
        'taxon_kingdom',
        'taxon_phylum',
        'taxon_class',
        'taxon_order',
        'taxon_family',
        'taxon_genus',
        # 'taxon_species',
        'chromosome_number',
        'haploid_number',
        'ploidy',
        'taxon_id',
        'c_value',
        'genome_size'
    )

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
# Register your models here.
# @register(CommonNames)
# class CommonNamesAdmin(admin.ModelAdmin):
#     list_display = (
#         'species',
#         'name'
#     )



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
    list_filter = admin.ModelAdmin.list_filter + ('species__tags',)
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

def update_specimens(modeladmin, request, queryset):
    if 'nagoya_statement' in request.POST:
        nagoya_statement = request.POST['nagoya_statement']
        queryset.update(nagoya_statement=nagoya_statement)
    messages.add_message(request, messages.INFO, 'Successfully updated specimen(s).')

@register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    save_as = True
    list_filter = admin.ModelAdmin.list_filter + ('species__tags',)
    action_form = SpecimenUpdateActionForm
    actions = [update_specimens]
    def get_actions(self, request):
      actions = super(SpecimenAdmin, self).get_actions(request)
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



admin.site.register(CommonNames)
admin.site.register(Synonyms)
admin.site.register(AssemblyTeam)
admin.site.register(Statement)
admin.site.register(AssemblyProject)
admin.site.register(Assembly)
admin.site.register(CollectionTeam)
admin.site.register(SampleCollection)
admin.site.register(CurationTeam)
admin.site.register(Curation)
# admin.site.register(SubmissionTeam)
# admin.site.register(Submission)
admin.site.register(SequencingTeam)
admin.site.register(VoucheringTeam)
admin.site.register(BarcodingTeam)
admin.site.register(TaxonomyTeam)
admin.site.register(SampleHandlingTeam)
admin.site.register(CommunityAnnotationTeam)
admin.site.register(BiobankingTeam)
admin.site.register(ExtractionTeam)
admin.site.register(Sequencing)
admin.site.register(Reads)
admin.site.register(AnnotationTeam)
admin.site.register(CommunityAnnotation)
admin.site.register(Annotation)
admin.site.register(BUSCOdb)
admin.site.register(BUSCOversion)
# admin.site.register(Specimen)
@register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = (
        'biosampleAccession',
        'collector_sample_id',
        'specimen',
        'species',
        'leftover'
    )
admin.site.register(AssemblyPipeline)
#admin.site.register(UserProfile)
#admin.site.register(GenomeTeam)
admin.site.register(Person)
#admin.site.register(Author)
admin.site.register(Affiliation)
admin.site.register(Role)
admin.site.register(Tag)
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
