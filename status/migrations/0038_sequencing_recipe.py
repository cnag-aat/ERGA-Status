# Generated by Django 3.0.2 on 2023-02-09 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0037_auto_20230209_1500'),
    ]

    operations = [
        migrations.AddField(
            model_name='sequencing',
            name='recipe',
            field=models.ForeignKey(default='HiFi25', null=True, on_delete=django.db.models.deletion.SET_NULL, to='status.Recipe', to_field='name', verbose_name='Recipe'),
        ),
    ]