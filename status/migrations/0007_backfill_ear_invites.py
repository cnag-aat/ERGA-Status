"""
Backfill EARAssignmentInvite rows for reviews that were assigned before
the invite model existed. All such assignments are treated as accepted
(the people are already actively on those reviews).
"""
from django.db import migrations
from django.utils import timezone


def backfill_invites(apps, schema_editor):
    EARReview = apps.get_model('status', 'EARReview')
    EARAssignmentInvite = apps.get_model('status', 'EARAssignmentInvite')

    for review in EARReview.objects.select_related('supervisor').prefetch_related('reviewers'):
        if review.supervisor_id:
            EARAssignmentInvite.objects.get_or_create(
                review=review,
                user_id=review.supervisor_id,
                role='supervisor',
                defaults={'status': 'accepted', 'responded_at': timezone.now()},
            )
        for reviewer in review.reviewers.all():
            EARAssignmentInvite.objects.get_or_create(
                review=review,
                user=reviewer,
                role='reviewer',
                defaults={'status': 'accepted', 'responded_at': timezone.now()},
            )


def reverse_backfill(apps, schema_editor):
    # On reversal simply remove all accepted invites created before now;
    # we can't distinguish them from real ones, so wipe the table.
    EARAssignmentInvite = apps.get_model('status', 'EARAssignmentInvite')
    EARAssignmentInvite.objects.filter(status='accepted').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('status', '0006_earassignmentinvite'),
    ]

    operations = [
        migrations.RunPython(backfill_invites, reverse_backfill),
    ]
