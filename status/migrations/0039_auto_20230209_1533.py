# Generated by Django 3.0.2 on 2023-02-09 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0038_sequencing_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sequencing',
            name='rnaseq_numlibs_target',
            field=models.IntegerField(blank=True, default=3, null=True, verbose_name='RNAseq libs target'),
        ),
    ]
