# Generated by Django 3.0.2 on 2023-01-24 10:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0009_auto_20230124_1103'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submissionteam',
            name='lead',
        ),
        migrations.RemoveField(
            model_name='submissionteam',
            name='members',
        ),
        migrations.DeleteModel(
            name='Submission',
        ),
        migrations.DeleteModel(
            name='SubmissionTeam',
        ),
    ]
