from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, world. You're at the status index.")
# Create your views here.
class TargetSpeciesListView(ExportMixin, SingleTableMixin, FilterView):
    # permission_required = "resistome.view_sample"
    # login_url = "access_denied"
    model = TargetSpecies
    table_class = TargetSpeciesTable
    template_name = 'targetspecies.html'
    filterset_class = SpeciesFilter
    table_pagination = {"per_page": 15}
