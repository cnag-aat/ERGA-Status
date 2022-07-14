from rest_framework import serializers
from status.models import *
from rest_framework_bulk import BulkSerializerMixin

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

class AssemblySerializerSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assembly
        fields = '__all__'
