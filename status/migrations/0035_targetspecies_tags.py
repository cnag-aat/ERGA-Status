# Generated by Django 3.0.2 on 2023-02-07 21:07

from django.db import migrations
import tagging.fields


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0034_auto_20230207_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='targetspecies',
            name='tags',
            field=tagging.fields.TagField(blank=True, max_length=255),
        ),
    ]