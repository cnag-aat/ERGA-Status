from django.conf import settings as django_settings
from .models import Customization


def customization(request):
    try:
        custom = Customization.objects.first()
    except Customization.DoesNotExist:
        custom = None
    palette = (
        custom.pill_palette
        if custom and custom.pill_palette
        else getattr(django_settings, 'PILL_PALETTE', 'original')
    )
    return {'custom': custom, 'PILL_PALETTE': palette}


def dashboard_action_count(request):
    """
    Adds `dashboard_action_count` to every template context.
    Counts items that require the user's immediate attention:
    pending invites + EARs to review + EARs awaiting supervisor decision.
    """
    if not request.user.is_authenticated:
        return {'dashboard_action_count': 0}

    from .models import EARAssignmentInvite, EARReview

    pending_invites = EARAssignmentInvite.objects.filter(
        user=request.user, status='pending'
    ).count()

    ears_to_review = EARReview.objects.filter(
        reviewers=request.user, status__in=['submitted', 'in_review']
    ).count()

    ears_awaiting_decision = EARReview.objects.filter(
        supervisor=request.user, status='reviewer_approved'
    ).count()

    total = pending_invites + ears_to_review + ears_awaiting_decision
    return {'dashboard_action_count': total}
