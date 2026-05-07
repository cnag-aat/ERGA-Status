from django.db import migrations


def create_ear_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.get_or_create(name='ear_reviewer')
    Group.objects.get_or_create(name='ear_supervisor')


def delete_ear_groups(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name__in=['ear_reviewer', 'ear_supervisor']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0003_auto_20260429_1704'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_ear_groups, reverse_code=delete_ear_groups),
    ]
