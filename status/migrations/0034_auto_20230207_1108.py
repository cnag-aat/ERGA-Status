# Generated by Django 3.0.2 on 2023-02-07 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0033_remove_samplecollection_team'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='annotation',
            name='team',
        ),
        migrations.RemoveField(
            model_name='communityannotation',
            name='team',
        ),
        migrations.RemoveField(
            model_name='curation',
            name='team',
        ),
    ]
