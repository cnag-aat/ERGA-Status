# Generated by Django 3.0.2 on 2023-03-02 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0054_auto_20230302_1240'),
    ]

    operations = [
        migrations.AddField(
            model_name='biobankingteam',
            name='institution',
            field=models.ManyToManyField(to='status.Affiliation'),
        ),
    ]
