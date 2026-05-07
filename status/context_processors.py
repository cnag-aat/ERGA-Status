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

    from django.db.models import Q, F, OuterRef, Subquery
    from .models import EARAssignmentInvite, EARReview, EARPdfVersion, EARComment

    pending_invites = EARAssignmentInvite.objects.filter(
        user=request.user, status='pending'
    ).count()

    ears_to_review = EARReview.objects.filter(
        reviewers=request.user, status__in=['submitted', 'in_review']
    ).count()

    ears_awaiting_decision = EARReview.objects.filter(
        supervisor=request.user, status='reviewer_approved'
    ).count()

    # Reviews where user is supervisor or reviewer and a PDF was replaced
    # after their last comment (or they haven't commented at all).
    latest_pdf_subq = EARPdfVersion.objects.filter(
        review=OuterRef('pk'),
    ).exclude(
        uploaded_by=request.user,
    ).order_by('-uploaded_at').values('uploaded_at')[:1]

    latest_comment_subq = EARComment.objects.filter(
        review=OuterRef('pk'),
        author=request.user,
        is_system=False,
    ).order_by('-created_at').values('created_at')[:1]

    ear_pdf_updates = (
        EARReview.objects
        .filter(Q(supervisor=request.user) | Q(reviewers=request.user))
        .annotate(
            latest_pdf=Subquery(latest_pdf_subq),
            latest_comment=Subquery(latest_comment_subq),
        )
        .filter(latest_pdf__isnull=False)
        .exclude(latest_comment__gte=F('latest_pdf'))
        .distinct()
        .count()
    )

    total = pending_invites + ears_to_review + ears_awaiting_decision + ear_pdf_updates
    return {
        'dashboard_action_count': total,
        'ear_pdf_updates_count': ear_pdf_updates,
    }
