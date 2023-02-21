from django.contrib import admin
from django.contrib.admin.decorators import register
from status.models import *
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

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
    list_filter = UserAdmin.list_filter + ('groups__name',)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'group')

@register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'author',
        'species',
        'role'
    )
@register(GenomeTeam)
class GenomeTeamAdmin(admin.ModelAdmin):
    save_as = True

admin.site.register(CommonNames)
admin.site.register(Synonyms)
admin.site.register(AssemblyTeam)

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
admin.site.register(Specimen)
admin.site.register(Sample)
admin.site.register(AssemblyPipeline)
admin.site.register(UserProfile)
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
# admin.site.unregister(User)
# admin.site.register(User, MyUserAdmin)
