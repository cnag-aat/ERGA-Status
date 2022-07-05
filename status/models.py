from django.db import models
import os
from django.conf import settings


# Create your models here.
class TargetSpecies(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    tolid_prefix = models.CharField(max_length=12, blank=True, null=True)

    class Meta:
        verbose_name_plural = 'species'

    def __str__(self):
        return self.name

class CommonNames(models.Model):
    species = models.ForeignKey(TargetSpecies, on_delete=models.CASCADE, verbose_name="Genus/species")
    common_name = models.CharField(max_length=200)

    class Meta:
        verbose_name_plural = 'common names'

    def __str__(self):
        return self.name
