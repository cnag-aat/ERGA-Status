from django.urls import path

from . import views
from status.views import TargetSpeciesListView

urlpatterns = [
    path('', views.index, name='index'),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
]
