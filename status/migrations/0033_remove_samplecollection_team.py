# Generated by Django 3.0.2 on 2023-02-07 09:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0032_sample_species'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='samplecollection',
            name='team',
        ),
    ]