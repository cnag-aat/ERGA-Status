from rest_framework import serializers
from status.models import *
from rest_framework_bulk import BulkSerializerMixin


class TargetSpeciesSerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TargetSpecies
        fields = '__all__'

class AssemblySerializer(BulkSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Assembly
        fields = '__all__'
