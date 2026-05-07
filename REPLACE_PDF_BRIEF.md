# EAR PDF Replacement — Project Brief

**Status: COMPLETE** — implemented, tested, committed (generalized branch, 2df8228), and deployed to production (cbp/).

## Goal

Add a "Replace EAR" action on the EAR review detail page that lets a submitter upload a new version of the EAR PDF mid-review (e.g. after a new assembly is produced), without restarting the review. Mirrors the GitHub workflow at https://github.com/ERGA-consortium/EARs where a PR can be updated with a new commit.

## Decisions

- **Permission:** any user in the species' assembly team (`species__gt_rel__assembly_team__members__user`). Superuser also allowed.
- **Versioning:** all prior PDFs kept in `EARPdfVersion`. `EARReview.ear_pdf` continues to point to the current file (backward-compat).
- **Thread entry:** auto-post a system `EARComment` with `is_system=True` for distinct muted/italic styling.
- **Notifications:** email supervisor + reviewers (exclude actor); dashboard counter; "Updated" badge on review page. Email skipped silently for users with no email address.
- **Status:** review status is **not** changed by a replacement.

## What was built

| Step | File(s) | Notes |
|------|---------|-------|
| 1. Model + migration | `status/models.py`, `status/migrations/0007_auto_20260507_1349.py` | `EARPdfVersion`, `EARComment.is_system`; backfill migration creates one version per existing EAR |
| 2. Form | `status/forms.py` — `EARPdfReplaceForm` | PDF-only validation, optional note |
| 3. View + URL | `status/views.py` — `ear_review_replace_pdf`, `_can_replace_pdf`; `status/urls.py` | `transaction.atomic()` wraps version swap + system comment |
| 4. Notification | `status/ear_review.py` — `notify_pdf_replaced`; `notify_assignment` early-return if no email | Silent skip for no-email users |
| 5. Dashboard counter | `status/context_processors.py` — `ear_pdf_updates` subquery in `dashboard_action_count` | Counts reviews where PDF was replaced after user's last comment |
| 6. EAR detail template | `status/templates/ear_review_detail.html` | Replace button → Bootstrap modal (gotcha #3 workaround); version history `<details>`; "Updated" badge; system comment styling |
| 7. Dashboard template | `status/templates/dashboard.html` | "EARs with updated PDF" card; empty-state guard updated |

## Gotchas encountered during implementation

- `.env` approach for deployment config: `erga/settings.py` and `erga/wsgi.py` are now fully generic; all deployment values in `erga/.env` (gitignored). See `erga/.env.template`.
- `ACCOUNT_UNIQUE_EMAIL` must stay `True` — see CLAUDE.md gotcha #10.
- `populate() isn't reentrant` requires Apache restart, not just wsgi touch — see CLAUDE.md gotcha #9.
- `tables.py render_task` returning `None` crashes species/collection pages — fixed; see CLAUDE.md gotcha #8.
- Production sync: copy `status/*.py`, templates, migration to `cbp/`; run `python manage.py migrate`; touch `cbp/erga/wsgi.py`.
