# Generated by Django 3.0.2 on 2023-02-21 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0047_auto_20230221_1336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotationteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='annotation_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='annotationteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='annotationteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='assemblyteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assembly_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='assemblyteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='assemblyteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='barcodingteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='barcoding_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='barcodingteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='barcodingteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='biobankingteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='biobanking_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='biobankingteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='biobankingteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='communityannotationteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='community_annotation_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='communityannotationteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='communityannotationteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='curationteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='curation_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='curationteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='curationteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='extractionteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='extraction_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='extractionteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='extractionteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='samplehandlingteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sample_handling_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='samplehandlingteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='samplehandlingteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='sequencingteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sequencing_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='sequencingteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='sequencingteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='taxonomyteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='taxonomy_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='taxonomyteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='taxonomyteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='voucheringteam',
            name='lead',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='vouchering_team_lead', to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='voucheringteam',
            name='members',
            field=models.ManyToManyField(blank=True, null=True, to='status.UserProfile'),
        ),
        migrations.AlterField(
            model_name='voucheringteam',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
