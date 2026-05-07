"""
EAR review business logic: reviewer/supervisor selection and notifications.

Selection algorithm (adapted from the GitHub-bot version at
https://github.com/ERGA-consortium/EARs/blob/main/rev/get_EAR_reviewer.py):

For each candidate reviewer in the `ear_reviewer` group:
  base score   = UserProfile.calling_score (default 1000)
  +50          if the user has never reviewed (no accepted EARReviews)
  -20          per active review (status in: in_review, reviewer_approved)
  -5           if the user is also in `ear_supervisor`
  excluded     if same research_group as submitter (COI)

Sort: score DESC, total_reviews ASC, last_review oldest-first, random tiebreaker.
"""

import logging
import random

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core import signing
from django.core.mail import send_mail
from django.db.models import Count, Max, Q

_ASSIGNMENT_SALT = 'ear-assignment'
_ASSIGNMENT_MAX_AGE = 7 * 24 * 3600  # 7 days

logger = logging.getLogger('status')


# ─────────────────────── Selection helpers ──────────────────────────────────

def _candidate_pool(group_name, exclude_user_ids=()):
    """Return active users in `group_name`, excluding given user ids."""
    try:
        group = Group.objects.get(name=group_name)
    except Group.DoesNotExist:
        return User.objects.none()
    return (
        User.objects
        .filter(is_active=True, groups=group)
        .exclude(id__in=exclude_user_ids)
    )


def _submitter_research_group(review):
    """Return the submitter's research_group, or None."""
    if not review.submitted_by:
        return None
    profile = getattr(review.submitted_by, 'user_profile', None)
    if profile and profile.exists():
        return profile.first().research_group
    return None


def select_supervisor(review):
    """
    Pick a supervisor from the `ear_supervisor` group.
    Excludes the submitter and any already-assigned reviewers.
    Random pick if multiple candidates.
    """
    excluded = [review.submitted_by_id] if review.submitted_by_id else []
    excluded += list(review.reviewers.values_list('id', flat=True))
    candidates = list(_candidate_pool('ear_supervisor', exclude_user_ids=excluded))
    if not candidates:
        return None
    return random.choice(candidates)


def select_reviewer(review, exclude_user_ids=()):
    """
    Score-based reviewer selection. Returns a User or None.

    `exclude_user_ids` lets the caller exclude already-assigned reviewers
    (so we can pick a second/third reviewer without re-picking the first).
    """
    from status.models import EARReview

    excluded = list(exclude_user_ids)
    if review.submitted_by_id:
        excluded.append(review.submitted_by_id)
    if review.supervisor_id:
        excluded.append(review.supervisor_id)

    submitter_rg = _submitter_research_group(review)

    pool = _candidate_pool('ear_reviewer', exclude_user_ids=excluded)

    # Conflict-of-interest: exclude same research group as submitter
    if submitter_rg:
        pool = pool.exclude(user_profile__research_group=submitter_rg)

    # Annotate with workload metrics
    pool = pool.annotate(
        total_accepted=Count(
            'ear_reviews',
            filter=Q(ear_reviews__status='accepted'),
            distinct=True,
        ),
        active_count=Count(
            'ear_reviews',
            filter=Q(ear_reviews__status__in=['in_review', 'reviewer_approved']),
            distinct=True,
        ),
        last_review=Max(
            'ear_reviews__updated_at',
            filter=Q(ear_reviews__status='accepted'),
        ),
    )

    supervisor_group_ids = set(
        User.objects.filter(groups__name='ear_supervisor').values_list('id', flat=True)
    )

    scored = []
    for user in pool:
        profile = user.user_profile.first() if user.user_profile.exists() else None
        base = profile.calling_score if profile else 1000

        score = base
        if user.total_accepted == 0:
            score += 50
        score -= 20 * user.active_count
        if user.id in supervisor_group_ids:
            score -= 5

        scored.append({
            'user': user,
            'score': score,
            'total_accepted': user.total_accepted,
            'last_review': user.last_review,
        })

    if not scored:
        return None

    # Sort: score DESC, total_accepted ASC, last_review oldest first
    # `last_review=None` (never reviewed) sorts before any date
    scored.sort(key=lambda r: (
        -r['score'],
        r['total_accepted'],
        r['last_review'] or '',
    ))

    # Random tiebreaker on top tier
    top_score = scored[0]['score']
    top_tier = [r for r in scored if r['score'] == top_score]
    return random.choice(top_tier)['user']


# ─────────────────────── Auto-assignment ─────────────────────────────────────

def auto_assign_supervisor(review, save=True):
    """Assign a supervisor if none is set. Returns the supervisor or None."""
    if review.supervisor_id:
        return review.supervisor

    supervisor = select_supervisor(review)
    if supervisor:
        review.supervisor = supervisor
        if save:
            review.save(update_fields=['supervisor', 'updated_at'])
        logger.info(f"Auto-assigned supervisor {supervisor} to EARReview {review.pk}")
    else:
        logger.warning(f"No supervisor candidates found for EARReview {review.pk}")
    return supervisor


def auto_assign_reviewer(review, added_by=None):
    """Add one reviewer to the review if none are assigned. Returns the reviewer or None."""
    from status.models import EARReviewer

    if review.reviewers.exists():
        return None

    reviewer = select_reviewer(review)
    if reviewer:
        EARReviewer.objects.create(
            review=review,
            reviewer=reviewer,
            added_by=added_by,
        )
        logger.info(f"Auto-assigned reviewer {reviewer} to EARReview {review.pk}")
    else:
        logger.warning(f"No reviewer candidates found for EARReview {review.pk}")
    return reviewer


# ─────────────────────── Notifications ───────────────────────────────────────

def _send(subject, body, recipient_list):
    """Wrapper around send_mail with sane defaults and silent failure."""
    recipients = [r for r in recipient_list if r]
    if not recipients:
        return
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=True,
        )
    except Exception as e:
        logger.error(f"Failed to send EAR notification: {e}")


def _display_name(user):
    """Best-effort full name for emails. Falls back through profile → User → username."""
    if not user:
        return 'unknown'
    profile = getattr(user, 'user_profile', None)
    if profile and profile.exists():
        p = profile.first()
        full = f"{p.first_name or ''} {p.last_name or ''}".strip()
        if full:
            return full
    full = user.get_full_name().strip()
    return full or user.username


def _make_assignment_token(review, user, role):
    """Return a signed token encoding (review_id, user_id, role)."""
    return signing.dumps(
        {'review': review.pk, 'user': user.pk, 'role': role},
        salt=_ASSIGNMENT_SALT,
    )


def load_assignment_token(token):
    """Decode and validate a token. Returns dict or raises signing.BadSignature."""
    return signing.loads(token, salt=_ASSIGNMENT_SALT, max_age=_ASSIGNMENT_MAX_AGE)


def _assignment_url(review, user, role, response):
    base = settings.DEFAULT_DOMAIN.rstrip('/')
    token = _make_assignment_token(review, user, role)
    return f"{base}/ear/assignment/{token}/{response}/"


def create_or_refresh_invite(review, user, role):
    """
    Create or reset an EARAssignmentInvite for this (review, user, role).
    Called every time an assignment is made so the dashboard can surface pending invites.
    If the same person is re-invited (rare), status resets to pending.
    """
    from status.models import EARAssignmentInvite
    invite, created = EARAssignmentInvite.objects.get_or_create(
        review=review,
        user=user,
        role=role,
        defaults={'status': 'pending'},
    )
    if not created and invite.status != 'pending':
        invite.status = 'pending'
        invite.responded_at = None
        invite.save(update_fields=['status', 'responded_at'])
    return invite


def mark_invite_responded(review, user, role, accepted):
    """Mark an existing invite as accepted or declined (idempotent)."""
    from django.utils import timezone
    from status.models import EARAssignmentInvite
    EARAssignmentInvite.objects.filter(review=review, user_id=user, role=role).update(
        status='accepted' if accepted else 'declined',
        responded_at=timezone.now(),
    )


def notify_assignment(review, user, role):
    """Create the invite record and, if the user has an email, send an assignment notification."""
    create_or_refresh_invite(review, user, role)
    if not user.email:
        return
    species = review.assembly_project.species if review.assembly_project else 'unknown species'
    submitter = _display_name(review.submitted_by)
    detail_url = f"{settings.DEFAULT_DOMAIN.rstrip('/')}/ear/{review.pk}/"
    yes_url = _assignment_url(review, user, role, 'yes')
    no_url  = _assignment_url(review, user, role, 'no')

    if role == 'supervisor':
        role_label = 'supervisor'
        question = 'Do you agree to supervise this EAR review?'
    else:
        role_label = 'reviewer'
        question = 'Do you agree to review this EAR?'

    subject = f"[ERGA-GTC] EAR {role_label} assignment: {species}"
    body = (
        f"You have been assigned as {role_label} for an EAR review.\n\n"
        f"Species:      {species}\n"
        f"Submitted by: {submitter}\n\n"
        f"{question}\n\n"
        f"  Yes, I accept:  {yes_url}\n"
        f"  No, reassign:   {no_url}\n\n"
        f"View the review: {detail_url}\n"
        f"(Links expire in 7 days)\n"
    )
    _send(subject, body, [user.email])


def notify_review_submitted(review):
    """Send assignment emails to the supervisor and any assigned reviewers."""
    if review.supervisor and review.supervisor.email:
        notify_assignment(review, review.supervisor, 'supervisor')
    for reviewer in review.reviewers.all():
        if reviewer.email:
            notify_assignment(review, reviewer, 'reviewer')


def notify_new_comment(comment):
    """Email all participants except the comment author when a new comment is posted."""
    review = comment.review
    species = review.assembly_project.species if review.assembly_project else 'unknown species'
    author = _display_name(comment.author)
    detail_url = f"{settings.DEFAULT_DOMAIN}ear/{review.pk}/"

    subject = f"[ERGA-GTC] New comment on EAR review: {species}"
    body_excerpt = (comment.body[:300] + '…') if len(comment.body) > 300 else comment.body
    body = (
        f"{author} commented on the EAR review for {species}:\n\n"
        f"{body_excerpt}\n\n"
        f"View the discussion: {detail_url}\n"
    )

    recipients = set()
    if review.submitted_by and review.submitted_by.email:
        recipients.add(review.submitted_by.email)
    if review.supervisor and review.supervisor.email:
        recipients.add(review.supervisor.email)
    for r in review.reviewers.all():
        if r.email:
            recipients.add(r.email)
    # Don't notify the commenter
    if comment.author and comment.author.email:
        recipients.discard(comment.author.email)

    _send(subject, body, list(recipients))


def notify_pdf_replaced(review, actor, note):
    """Email supervisor and reviewers (excluding the actor) when the EAR PDF is replaced."""
    species = review.assembly_project.species if review.assembly_project else 'unknown species'
    actor_name = _display_name(actor)
    detail_url = f"{settings.DEFAULT_DOMAIN.rstrip('/')}/ear/{review.pk}/"

    subject = f"[ERGA-GTC] EAR PDF updated for {species}"
    body = (
        f"{actor_name} uploaded a new version of the EAR PDF for {species}.\n\n"
        + (f"Note: {note}\n\n" if note else "")
        + f"View the review: {detail_url}\n"
    )

    recipients = set()
    if review.supervisor and review.supervisor.email:
        recipients.add(review.supervisor.email)
    for r in review.reviewers.all():
        if r.email:
            recipients.add(r.email)
    if actor and actor.email:
        recipients.discard(actor.email)

    _send(subject, body, list(recipients))


def notify_status_change(review, previous_status):
    """Notify relevant parties when a review status changes."""
    species = review.assembly_project.species if review.assembly_project else 'unknown species'
    detail_url = f"{settings.DEFAULT_DOMAIN.rstrip('/')}/ear/{review.pk}/"
    subject = f"[ERGA-GTC] EAR review {review.get_status_display().lower()}: {species}"
    body = (
        f"EAR review status changed: {previous_status} → {review.status}\n\n"
        f"Species: {species}\n\n"
        f"View the review: {detail_url}\n"
    )

    recipients = []
    if review.submitted_by and review.submitted_by.email:
        recipients.append(review.submitted_by.email)
    if review.supervisor and review.supervisor.email:
        recipients.append(review.supervisor.email)
    for reviewer in review.reviewers.all():
        if reviewer.email:
            recipients.append(reviewer.email)

    _send(subject, body, recipients)
