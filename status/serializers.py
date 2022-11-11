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

class AssemblyTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssemblyTeam
        fields = '__all__'

class AssemblyProjectSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AssemblyProject
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

class SampleSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'

class CollectionTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CollectionTeam
        fields = '__all__'

class SampleCollectionSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SampleCollection
        fields = '__all__'

class SequencingSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Sequencing
        fields = '__all__'

class SequencingTeamSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SequencingTeam
        fields = '__all__'

class ReadsSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Reads
        fields = '__all__'

class UserSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
