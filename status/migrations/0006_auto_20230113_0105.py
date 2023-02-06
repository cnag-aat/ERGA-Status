# Generated by Django 3.0.2 on 2023-01-13 00:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0005_person_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='assemblyteam',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assemblyteam',
            name='modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]