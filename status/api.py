from status.models import *
from rest_framework import viewsets
from status.serializers import *
from rest_framework_bulk import BulkModelViewSet

class TaxonKingdomViewSet(BulkModelViewSet):
    """
    API endpoint that allows kingdoms to be viewed or edited.
    """
    queryset = TaxonKingdom.objects.all()
    serializer_class = TaxonKingdomSerializer
    filter_fields = '__all__'

class TaxonPhylumViewSet(BulkModelViewSet):
    """
    API endpoint that allows phyla to be viewed or edited.
    """
    queryset = TaxonPhylum.objects.all()
    serializer_class = TaxonPhylumSerializer
    filter_fields = '__all__'

class TaxonClassViewSet(BulkModelViewSet):
    """
    API endpoint that allows classes to be viewed or edited.
    """
    queryset = TaxonClass.objects.all()
    serializer_class = TaxonClassSerializer
    filter_fields = '__all__'

class TaxonOrderViewSet(BulkModelViewSet):
    """
    API endpoint that allows orders to be viewed or edited.
    """
    queryset = TaxonOrder.objects.all()
    serializer_class = TaxonOrderSerializer
    filter_fields = '__all__'

class TaxonFamilyViewSet(BulkModelViewSet):
    """
    API endpoint that allows families to be viewed or edited.
    """
    queryset = TaxonFamily.objects.all()
    serializer_class = TaxonFamilySerializer
    filter_fields = '__all__'

class TaxonGenusViewSet(BulkModelViewSet):
    """
    API endpoint that allows genera to be viewed or edited.
    """
    queryset = TaxonGenus.objects.all()
    serializer_class = TaxonGenusSerializer
    filter_fields = '__all__'



class TargetSpeciesViewSet(BulkModelViewSet):
    """
    API endpoint that allows target species to be viewed or edited.
    """
    queryset = TargetSpecies.objects.all()
    serializer_class = TargetSpeciesSerializer
    filter_fields = '__all__'

class AssemblyTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows assembly teams to be viewed or edited.
    """
    queryset = AssemblyTeam.objects.all()
    serializer_class = AssemblyTeamSerializer
    filter_fields = '__all__'

class AssemblyProjectViewSet(BulkModelViewSet):
    """
    API endpoint that allows assembly projects to be viewed or edited.
    """
    queryset = AssemblyProject.objects.all()
    serializer_class = AssemblyProjectSerializer
    filter_fields = '__all__'

class AssemblyViewSet(BulkModelViewSet):
    """
    API endpoint that allows assemblies to be viewed or edited.
    """
    queryset = Assembly.objects.all()
    serializer_class = AssemblySerializer
    filter_fields = '__all__'
