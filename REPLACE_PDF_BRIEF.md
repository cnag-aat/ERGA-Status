# EAR PDF Replacement — Project Brief

## Goal

Add a "Replace EAR" action on the EAR review detail page that lets a submitter upload a new version of the EAR PDF mid-review (e.g. after a new assembly is produced), without restarting the review. Mirrors the GitHub workflow at https://github.com/ERGA-consortium/EARs where a PR can be updated with a new commit.

## Decisions

- **Permission:** any user in the species' assembly team (same rule as initial submission — `species__gt_rel__assembly_team__members__user`). Superuser also allowed.
- **Versioning:** keep all prior PDFs in a new `EARPdfVersion` model. `EARReview.ear_pdf` continues to point to the current file (backward-compat).
- **Thread entry:** auto-post a system `EARComment` ("X replaced the EAR PDF[: <note>]"). Add `EARComment.is_system` boolean for distinct styling.
- **Notifications:** all three —
  1. email supervisor + reviewers (exclude actor)
  2. bump dashboard counter
  3. "updated" badge on the review page
- **Status:** review status is **not** changed by a replacement.

## Changes

### 1. Model — `status/models.py`

```python
class EARPdfVersion(models.Model):
    review      = FK(EARReview, related_name='pdf_versions', on_delete=CASCADE)
    file        = FileField(upload_to='ear_pdfs/versions/')
    uploaded_by = FK(User, on_delete=PROTECT)
    uploaded_at = DateTimeField(auto_now_add=True)
    note        = CharField(max_length=255, blank=True)
    is_current  = BooleanField(default=True)
    class Meta:
        ordering = ['-uploaded_at']
```

Add `EARComment.is_system = BooleanField(default=False)`.

Add `EARReview.current_pdf_version` helper property (latest `is_current=True`).

**Backfill data migration:** for every `EARReview` with a non-empty `ear_pdf`, create `EARPdfVersion(file=review.ear_pdf, uploaded_by=review.submitted_by, uploaded_at=review.created_at, is_current=True)`.

### 2. Form — `status/forms.py`

`EARPdfReplaceForm(forms.Form)`:
- `ear_pdf` — `FileField`, `accept='.pdf'`, same size validation as `EARReviewCreateForm` (forms.py:104–166)
- `note` — optional `CharField(max_length=255, required=False)`

### 3. View — `status/views.py` (append at bottom near other EAR views, ~line 1755)

`ear_review_replace_pdf(request, pk)` — POST-only, login required:

1. `review = get_object_or_404(EARReview, pk=pk)`
2. Permission: user in `AssemblyTeam.objects.filter(members__user=user, genometeam__species=review.assembly_project.species)` OR `is_superuser`. Otherwise 403.
3. Bind `EARPdfReplaceForm(request.POST, request.FILES)`. Invalid → `messages.error` + redirect.
4. `transaction.atomic()`:
   - Mark all existing `EARPdfVersion` rows for this review `is_current=False`.
   - Create new `EARPdfVersion(...)` with `is_current=True`.
   - `review.ear_pdf = new_version.file`; `review.save(update_fields=['ear_pdf', 'updated_at'])`.
   - Create `EARComment(review=review, author=request.user, body="Replaced the EAR PDF" + (": "+note if note else ""), is_system=True)`.
5. Outside the transaction: `notify_pdf_replaced(review, request.user, note)`.
6. `messages.success` + redirect to `ear_review_detail`.

URL in `status/urls.py`:
```python
path('ear/<int:pk>/replace-pdf/', views.ear_review_replace_pdf, name='ear_review_replace_pdf'),
```

### 4. Notification — `status/ear_review.py`

`notify_pdf_replaced(review, actor, note)` — clone of `notify_new_comment` (ear_review.py:311):
- subject: `[EAR] PDF updated for <species>`
- body: short message + link to review detail + optional note excerpt
- recipients: supervisor + reviewers, excluding `actor`
- uses existing `_send()` wrapper (ear_review.py:192)

### 5. Dashboard counter — `status/context_processors.py`

Extend `dashboard_action_count` (lines 18–42) with a 4th key, `ear_pdf_updates_count`:

Count `EARReview` rows where:
- user is supervisor or reviewer, AND
- the most recent `EARPdfVersion` (`exclude(uploaded_by=user)`) was uploaded **after** the user's most recent `EARComment` on that review.

Cheap approximation — "PDF was replaced and you haven't commented since." Skip for anonymous users (consistent with existing pattern).

### 6. Template — `status/templates/ear_review_detail.html`

Around current PDF link (lines ~118–123):

- **Replace EAR button** (visible only to assembly team members + superuser): opens a Bootstrap modal with the upload form + note textarea, POSTs to `ear_review_replace_pdf`. Use the hidden `data-toggle="modal"` button + native `.click()` workaround (CLAUDE.md gotcha #3).
- **Previous versions** expandable list iterating `review.pdf_versions.all()` — date, uploader, download link; current marked "current".
- **"Updated" badge** when more than one `EARPdfVersion` exists.
- **System comments**: render in muted/italic style with a `bi-arrow-repeat` icon when `comment.is_system`.

### 7. Dashboard template

Surface `ear_pdf_updates_count` next to existing counters (`pending_invites_count`, `awaiting_supervisor_count`, etc.) — find via grep in `status/templates/`.

## Critical files

- `status/models.py` — `EARPdfVersion`, `EARComment.is_system`, `EARReview.current_pdf_version`
- `status/forms.py` — `EARPdfReplaceForm`
- `status/views.py` — `ear_review_replace_pdf` (~line 1755)
- `status/urls.py` — new route
- `status/ear_review.py` — `notify_pdf_replaced` (alongside `notify_new_comment`)
- `status/context_processors.py` — extend `dashboard_action_count`
- `status/templates/ear_review_detail.html` — button, modal, version list, badge, system comment styling
- Dashboard template(s) — surface new counter
- Migrations: schema + data backfill

## Reuse

- `_can_post_on_review()` (views.py:1638) — reference; write parallel `_can_replace_pdf()`.
- `notify_new_comment()` (ear_review.py:311) — clone for `notify_pdf_replaced`.
- `_send()` (ear_review.py:192) — email wrapper.
- `EARReviewCreateForm` PDF validation (forms.py:104–166).
- Bootstrap modal workaround (CLAUDE.md gotcha #3).

## Working rules

- Step-by-step: implement and pause for user testing after each numbered step (model + migration first, then form/view/url, then notification, then dashboard counter, then template).
- Files only inside `ear-review/` unless explicitly authorized.
- `mariadb` not `mysql`; DB password via `~/.mydev.cnf`.
- Reload after Python changes: `touch erga/wsgi.py`. Log: `~/logs/ear-review-dev.log`.
- Use dev settings: `--settings=erga.settings_dev`.
- venv: `/home/www/resistome.cnag.cat/virtualenvs/incredble_venv`.

## Verification

1. **Migrations**
   ```bash
   source /home/www/resistome.cnag.cat/virtualenvs/incredble_venv/bin/activate
   python manage.py makemigrations --settings=erga.settings_dev
   python manage.py migrate --settings=erga.settings_dev
   ```
   Confirm: `EARPdfVersion.objects.count()` equals number of `EARReview` rows with a non-empty `ear_pdf`.

2. **Reload:** `touch erga/wsgi.py`; tail `~/logs/ear-review-dev.log`.

3. **Manual end-to-end** at `https://genomes.cnag.cat/cbp-dev/ear/<pk>/`:
   - As assembly team member → "Replace EAR" button visible. Upload new PDF + note → success; PDF link points to new file; previous version in "Previous versions"; system comment in thread; "Updated" badge shows.
   - As supervisor/reviewer → button hidden; receives email; dashboard counter +1; after they comment, counter clears.
   - As unrelated user → button hidden; direct POST returns 403.
   - Original PDF still downloadable from versions list.
   - Review status unchanged after replacement.

4. **Static** (only if new CSS/JS): `python manage.py collectstatic --settings=erga.settings_dev --noinput`.

5. **Upload size:** Apache/ModSecurity already exempts `/cbp-dev/ear/` paths for 500MB limit (CLAUDE.md).
