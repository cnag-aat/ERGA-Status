# Generated by Django 3.0.2 on 2023-02-27 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0050_targetspecies_listed_species'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='tag',
            field=models.CharField(default='erga_long_list', max_length=50),
        ),
        migrations.AlterField(
            model_name='targetspecies',
            name='tags',
            field=models.ManyToManyField(default='erga_long_list', to='status.Tag'),
        ),
    ]
