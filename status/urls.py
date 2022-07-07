from django.urls import path

from . import views
from status.views import TargetSpeciesListView

urlpatterns = [
    path('', views.index, name='index'),
    path("", HomeView.as_view(), name="home"),
    path("species/", TargetSpeciesListView.as_view(), name="species_list"),
]
