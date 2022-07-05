from status.models import *
from rest_framework import viewsets
from status.serializers import *
from rest_framework_bulk import BulkModelViewSet


class TargetSpeciesViewSet(BulkModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TargetSpecies.objects.all()
    serializer_class = TargetSpeciesSerializer
    filter_fields = '__all__'
