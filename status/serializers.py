from rest_framework import serializers
from status.models import *
from rest_framework_bulk import BulkSerializerMixin
from django.contrib.auth.models import User

class TaxonKingdomSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonKingdom
        fields = '__all__'

class TaxonPhylumSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonPhylum
        fields = '__all__'

class TaxonClassSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonClass
        fields = '__all__'

class TaxonOrderSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonOrder
        fields = '__all__'

class TaxonFamilySerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonFamily
        fields = '__all__'

class TaxonGenusSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonGenus
        fields = '__all__'

class TargetSpeciesSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TargetSpecies
        fields = '__all__'

class SubSpeciesSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SubSpecies
        fields = '__all__'

class AssemblyTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssemblyTeam
        fields = '__all__'

class AssemblyProjectSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssemblyProject
        fields = '__all__'

class AssemblyPipelineSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssemblyPipeline
        fields = '__all__'

class AssemblySerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assembly
        fields = '__all__'

class BUSCOdbSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BUSCOdb
        fields = '__all__'

class BUSCOversionSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BUSCOversion
        lookup_field = 'version'
        fields = '__all__'

class StatementSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Statement
        lookup_field = 'name'
        fields = '__all__'

class SampleSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class SpecimenSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Specimen
        fields = '__all__'

class CollectionTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionTeam
        fields = '__all__'

class SampleCollectionSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SampleCollection
        fields = '__all__'

class SampleHandlingTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SampleHandlingTeam
        fields = '__all__'

class TaxonomyTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TaxonomyTeam
        fields = '__all__'

class BarcodingTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BarcodingTeam
        fields = '__all__'

class ExtractionTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExtractionTeam
        fields = '__all__'

class CommunityAnnotationTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CommunityAnnotationTeam
        fields = '__all__'

class AnnotationTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AnnotationTeam
        fields = '__all__'

class SequencingSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sequencing
        fields = '__all__'

class SequencingTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SequencingTeam
        fields = '__all__'

class HiCTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HiCTeam
        fields = '__all__'

class BiobankingTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BiobankingTeam
        fields = '__all__'

class VoucheringTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = VoucheringTeam
        fields = '__all__'

class FromManifestSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FromManifest
        fields = '__all__'

class GenomeTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GenomeTeam
        fields = '__all__'

class ReadsSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reads
        fields = '__all__'

class EnaReadsSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnaReads
        fields = '__all__'

class RunSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Run
        fields = '__all__'

class EnaRunSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EnaRun
        fields = '__all__'

class UserSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

# class TagSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = Tag
#         fields = '__all__'

class RecipeSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'

class AffiliationSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Affiliation
        fields = '__all__'

class UserProfileSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class PhaseSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Phase
        fields = '__all__'

class TaskSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class CountrySerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class SubprojectSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Subproject
        fields = '__all__'

class PersonSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Person
        fields = '__all__'
