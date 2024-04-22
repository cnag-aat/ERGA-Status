from status.models import *
from rest_framework import viewsets
from status.serializers import *
from rest_framework_bulk import BulkModelViewSet

class PhaseViewSet(BulkModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    queryset = Phase.objects.all()
    serializer_class = PhaseSerializer
    filter_fields = '__all__'

class TaskViewSet(BulkModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_fields = '__all__'

class CountryViewSet(BulkModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    filter_fields = '__all__'

class SubprojectViewSet(BulkModelViewSet):
    """
    API endpoint that allows Users to be viewed or edited.
    """
    queryset = Subproject.objects.all()
    serializer_class = SubprojectSerializer
    filter_fields = '__all__'

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

class BUSCOversionViewSet(BulkModelViewSet):
    """
    API endpoint that allows BUSCO versions to be viewed or edited.
    """
    queryset = BUSCOversion.objects.all()
    serializer_class = BUSCOversionSerializer
    filter_fields = '__all__'

class BUSCOdbViewSet(BulkModelViewSet):
    """
    API endpoint that allows BUSCO dbs to be viewed or edited.
    """
    queryset = BUSCOdb.objects.all()
    serializer_class = BUSCOdbSerializer
    filter_fields = '__all__'

class StatementViewSet(BulkModelViewSet):
    """
    API endpoint that allows Statements to be viewed or edited.
    """
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer
    filter_fields = '__all__'

class SpecimenViewSet(BulkModelViewSet):
    """
    API endpoint that allows Specimen to be viewed or edited.
    """
    queryset = Specimen.objects.all()
    serializer_class = SpecimenSerializer
    filter_fields = '__all__'

class SampleViewSet(BulkModelViewSet):
    """
    API endpoint that allows Samples to be viewed or edited.
    """
    queryset = Sample.objects.all()
    serializer_class = SampleSerializer
    filter_fields = '__all__'

class SampleCollectionViewSet(BulkModelViewSet):
    """
    API endpoint that allows Sample Collection to be viewed or edited.
    """
    team = CollectionTeamSerializer()
    queryset = SampleCollection.objects.all()
    serializer_class = SampleCollectionSerializer
    filter_fields = '__all__'

class CollectionTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows Collection Team to be viewed or edited.
    """
    queryset = CollectionTeam.objects.all()
    serializer_class = CollectionTeamSerializer
    filter_fields = '__all__'

class SampleHandlingTeamViewset(BulkModelViewSet):
    """
    API endpoint that allows Collection Team to be viewed or edited.
    """
    queryset = SampleHandlingTeam.objects.all()
    serializer_class = SampleHandlingTeamSerializer
    filter_fields = '__all__'

class VoucheringTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows Collection Team to be viewed or edited.
    """
    queryset = VoucheringTeam.objects.all()
    serializer_class = VoucheringTeamSerializer
    filter_fields = '__all__'


class BiobankingTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = BiobankingTeam.objects.all()
    serializer_class = BiobankingTeamSerializer
    filter_fields = '__all__'

class SequencingViewSet(BulkModelViewSet):
    """
    API endpoint that allows Sequencing projects to be viewed or edited.
    """
    queryset = Sequencing.objects.all()
    serializer_class = SequencingSerializer
    filter_fields = '__all__'

class SequencingTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows Sequencing Team to be viewed or edited.
    """
    queryset = SequencingTeam.objects.all()
    serializer_class = SequencingTeamSerializer
    filter_fields = '__all__'

class BarcodingTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = BarcodingTeam.objects.all()
    serializer_class = BarcodingTeamSerializer
    filter_fields = '__all__'

class ExtractionTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = ExtractionTeam.objects.all()
    serializer_class = ExtractionTeamSerializer
    filter_fields = '__all__'

class CommunityAnnotationTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = CommunityAnnotationTeam.objects.all()
    serializer_class = CommunityAnnotationTeamSerializer
    filter_fields = '__all__'

class AnnotationTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = AnnotationTeam.objects.all()
    serializer_class = AnnotationTeamSerializer
    filter_fields = '__all__'

class TaxonomyTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows BiobankingTeam Team to be viewed or edited.
    """
    queryset = TaxonomyTeam.objects.all()
    serializer_class = TaxonomyTeamSerializer
    filter_fields = '__all__'

class GenomeTeamViewSet(BulkModelViewSet):
    """
    API endpoint that allows GenomeTeam Team to be viewed or edited.
    """
    queryset = GenomeTeam.objects.all()
    serializer_class = GenomeTeamSerializer
    filter_fields = '__all__'

class ReadsViewSet(BulkModelViewSet):
    """
    API endpoint that allows Reads to be viewed or edited.
    """
    queryset = Reads.objects.all()
    serializer_class = ReadsSerializer
    filter_fields = '__all__'

class RunViewSet(BulkModelViewSet):
    queryset = Run.objects.all()
    serializer_class = RunSerializer
    filter_fields = '__all__'

class UserViewSet(BulkModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_fields = '__all__'

class TagViewSet(BulkModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_fields = '__all__'

class RecipeViewSet(BulkModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_fields = '__all__'

class AffiliationViewSet(BulkModelViewSet):
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    filter_fields = '__all__'

class UserProfileViewSet(BulkModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    filter_fields = '__all__'

class PersonViewSet(BulkModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_fields = '__all__'
