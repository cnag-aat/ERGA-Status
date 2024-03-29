# Generated by Django 3.0.2 on 2023-01-24 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0010_auto_20230124_1145'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityAnnotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Waiting', 'Waiting'), ('Annotating', 'Annotating'), ('Done', 'Done'), ('Sent', 'Sent'), ('Issue', 'Issue')], default='Waiting', help_text='Status', max_length=12)),
                ('note', models.CharField(blank=True, help_text='Notes', max_length=300, null=True)),
                ('species', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='status.TargetSpecies', verbose_name='species')),
                ('team', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='status.AnnotationTeam', verbose_name='annotation team')),
            ],
        ),
    ]
