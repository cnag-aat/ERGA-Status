# EAR Review Feature — Project Brief

## Overview

Implementing an ERGA Assembly Report (EAR) review process inside the existing Django GTC app (`ear-review` branch), replacing the GitHub-workflow-based process at https://github.com/ERGA-consortium/EARs.

---

## Dev Environment (COMPLETE)

| Item | Value |
|------|-------|
| Branch | `ear-review` |
| Project dir | `/home/www/resistome.cnag.cat/ear-review/` |
| Dev database | `cbp_dev` (MariaDB, copied from `cbp`) |
| Dev settings | `erga/settings_dev.py` |
| Secrets | `erga/.env` (separate SECRET_KEY from production) |
| Dev URL | `https://genomes.cnag.cat/cbp-dev` |
| Static files | `/home/www/resistome.cnag.cat/incredible/deployment/static/` |
| Static URL | `/cbp-dev/static/` |
| Log | `~/logs/ear-review-dev.log` |
| venv | `/home/www/resistome.cnag.cat/virtualenvs/incredble_venv` |

### Key Apache directives (in resistome.cnag.cat-le-ssl.conf)
```apache
WSGIDaemonProcess cbp-dev-site python-home=/home/www/resistome.cnag.cat/virtualenvs/incredble_venv
WSGIProcessGroup cbp-dev-site
WSGIScriptAlias /cbp-dev /home/www/resistome.cnag.cat/ear-review/erga/wsgi.py process-group=cbp-dev-site
Alias /cbp-dev/static/ /home/www/resistome.cnag.cat/incredible/deployment/static/
<Directory "/home/www/resistome.cnag.cat/incredible/deployment/static">
    Require all granted
</Directory>
<Directory "/home/www/resistome.cnag.cat/ear-review">
    AllowOverride All
    Require all granted
</Directory>
<Directory "/home/www/resistome.cnag.cat/ear-review/erga">
    AllowOverride All
    Require all granted
</Directory>
```

### Useful dev commands
```bash
source /home/www/resistome.cnag.cat/virtualenvs/incredble_venv/bin/activate
cd /home/www/resistome.cnag.cat/ear-review

python manage.py runserver 0.0.0.0:8001 --settings=erga.settings_dev
python manage.py makemigrations --settings=erga.settings_dev
python manage.py migrate --settings=erga.settings_dev
python manage.py collectstatic --settings=erga.settings_dev --noinput
```

---

## Completed Work

### UserProfile additions (migrations 0002 + 0003)
- `research_group` — FK to new `ResearchGroup` model (short lab/PI name for COI checks)
  - Signup form, profile update form, and admin all use `AddAnotherWidgetWrapper` popup
  - `ResearchGroup` registered in admin
- `calling_score` — IntegerField, default 1000, used by reviewer selection algorithm
- `ACCOUNT_FORMS` fixed to `status.forms.CustomSignupForm`

### Signup / auth flow fixes
- `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'`
- `ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL` sends new users to login with `?next=/cbp-dev/edit_profile/`
- `EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL` for already-authenticated users
- Fixed hardcoded relative `static/` path in `base.html` (line 51)

### Groups (migration 0004)
- `ear_reviewer` and `ear_supervisor` groups created via data migration
- Submitters: any user in an `AssemblyTeam` (no group needed)
- UserProfile `roles` field retained as-is for admin reference only

### EAR review models (migration 0005)
- `EARReview` — assembly_project (OneToOne), submitted_by, supervisor, reviewers (M2M via through model), ear_pdf, pretext_file (nullable, deleted on acceptance), status, timestamps
- `EARReviewer` — through model with `added_by` and `added_at` (uses `through_fields`)
- `EARComment` — flat thread with optional `parent` FK
- `EARAttachment` — files on comments (screenshots, savestate, additional pretexts)
- All registered in admin with appropriate inlines, autocompletes, and `search_fields`
- Pretext file made writable: `deployment/data/{ear_pdfs,pretext,ear_attachments}/` (777)

### EAR review business logic (`status/ear_review.py`)
- `select_supervisor()` — random pick from `ear_supervisor` group
- `select_reviewer()` — score algorithm: calling_score (1000 base) +50 if never reviewed, −20 per active review, −5 if also supervisor; COI excludes same `research_group`; random tiebreaker
- `auto_assign_supervisor()` — fires from `post_save` signal on creation
- `auto_assign_reviewer()` — fires from admin `save_related` (after inlines saved)
- `notify_review_submitted()`, `notify_new_comment()`, `notify_status_change()` — email helpers via `settings.DEFAULT_FROM_EMAIL`

### AssemblyProject status sync
- `EAR_TO_ASSEMBLY_STATUS` mapping: submitted/in_review → `UnderReview`; reviewer_approved/accepted → `Approved`; rejected/declined → `UnderReview`
- Synced via `_sync_assembly_project_status()` in the post_save signal

### Detail page (`/cbp-dev/ear/<pk>/`)
- `EARReviewDetailView` (LoginRequiredMixin)
- Status banner (colour-coded), submission metadata, file download links
- Discussion thread with flat comments + indented replies
- GitHub PR-style comment form with multiple submit buttons:
  - **Comment** (any participant)
  - **Approve / Reject** (reviewer; reject requires comment)
  - **Accept / Decline** (supervisor; decline requires comment)
- Action permission validated server-side per role + current status
- Comment markers prepended (`✓ **Approved**`, `✗ **Rejected**`, etc.)
- Reply button on each comment (sets parent FK + scrolls to form)
- Multi-file attachments (images render inline, others as paperclip links)

### File / upload configuration
- `MEDIA_URL = '/cbp-dev/media/'`
- `DATA_UPLOAD_MAX_MEMORY_SIZE = 500 MB`, `FILE_UPLOAD_MAX_MEMORY_SIZE = 1 MB` (stream early)
- Apache vhost: `Alias /cbp-dev/media/`, `LimitRequestBody 524288000`, `SecRequestBodyLimit 524288000`, `WSGIDaemonProcess ... request-timeout=600`
- Pretext field stays nullable at the model level (so post-acceptance delete doesn't break validation); required-on-creation will be enforced at form level when we build the user-facing upload form

---

## Feature: EAR Review Process

### Requirements
1. Django user management (not GitHub)
2. Upload EAR (PDF) and pretextmap (200–300 MB binary) to kick off a review
3. Supervisor and reviewer selected from users with appropriate roles
4. Discussion thread — any logged-in user can view; only reviewer(s), supervisor, and submitter can post
5. Final approval by reviewer(s), accepted or rejected by supervisor
6. On acceptance: EAR PDF permanently attached to `AssemblyProject`; pretext file deleted from server
7. Additional file uploads per review: pretext savestate file, screenshots (displayed in thread)

### Data Model Design

```
EARReview
  ├── assembly_project        FK → AssemblyProject
  ├── submitted_by            FK → User
  ├── supervisor              FK → User (nullable)
  ├── reviewers               ManyToMany → User (via through model — tracks who added whom)
  ├── ear_pdf                 FileField (permanent, stored in media/ear_pdfs/)
  ├── pretext_file            FileField (temporary, deleted on acceptance, media/pretext/)
  ├── status                  CharField choices (see workflow below)
  ├── created_at / updated_at DateTimeField

EARComment
  ├── review                  FK → EARReview
  ├── author                  FK → User
  ├── body                    TextField
  ├── parent                  FK → self (nullable, for optional threading)
  ├── attachments             (screenshots, savestate files — separate model)
  └── created_at              DateTimeField

EARAttachment
  ├── comment                 FK → EARComment
  ├── file                    FileField (media/ear_attachments/)
  └── uploaded_at             DateTimeField
```

### Workflow States
```
submitted → in_review → reviewer_approved → accepted
                      ↘ rejected (by reviewer)
                                          ↘ declined (by supervisor)
```

### Reviewer Selection Algorithm (adapted from GitHub bot)
Inputs per candidate in `ear_reviewer` group:
- `research_group` (COI check — must differ from submitter)
- `calling_score` on UserProfile (base 1000)
- Active reviews: COUNT of EARReviews in `in_review`/`reviewer_approved` assigned to them
- Total reviews: COUNT of accepted EARReviews
- Last review: MAX updated_at on accepted reviews

Score adjustments:
- **+50** if never reviewed (no accepted reviews)
- **-20** per active review (workload penalty)
- **-5** if also in `ear_supervisor` group
- Random tiebreaker

Supervisor can override and add additional reviewers.

### File Storage
- `media/ear_pdfs/` — permanent
- `media/pretext/` — deleted via post-save signal on acceptance
- `media/ear_attachments/` — screenshots and savestate files uploaded in comments
- Pretextmap files need to be downloadable (loaded locally with PretextView AI)
- Large file upload (200–300 MB) — confirm server upload limits with IT before implementing

---

## Architecture / Build Plan

### Phase 1 — EAR Review ✅ COMPLETE
1. ✅ Create `ear_reviewer` and `ear_supervisor` Django Groups
2. ✅ Create `EARReview`, `EARComment`, `EARAttachment` models + migration
3. ✅ Detail view: thread + status banner + action buttons
4. ✅ Role-gated action buttons: reviewer approves/rejects, supervisor accepts/declines
5. ✅ Post-save signal to delete pretext file on acceptance
6. ✅ AssemblyProject status sync
7. ✅ User-facing EAR upload form (`/ear/new/`)
8. ✅ EAR list view (`/ear/`) — filterable by species, status, submitter
9. ✅ Supervisor reviewer-management (add/remove from detail page)
10. ✅ Link accepted EAR PDF to `AssemblyProject` / species detail page
11. ✅ Assignment confirmation emails with Yes/No links (signed tokens, 7-day expiry, auto-reassign on decline)
12.  All notification links point to user-facing detail view (not admin)

### Phase 2 — Team-gated Editing ✅ COMPLETE

**Strategy (revised):** All users view all species. Editing is gated by team membership, not viewing.

**Permission model:**
- `User → UserProfile → AssemblyTeam.members (M2M) → GenomeTeam.assembly_team → GenomeTeam.species`
- Assembly team members can edit: `AssemblyProject.status`, `.note`, `.genome_size_estimate` for their species
- Sequencing team members can edit `Sequencing.long_seq_status`, `.short_seq_status`, `.hic_seq_status`, `.rna_seq_status`, `.note` for their species
- Superusers can edit everything

**What shipped:**
- `AssemblyProjectTable` and `SequencingTable` accept a `user` kwarg; `render_edit` shows the `✎` button only when the user is a member of the relevant team (or a superuser)
- POST views `assembly_project_edit` (`/projects/<pk>/edit/`) and `sequencing_edit` (`/sequencing/<pk>/edit/`) re-check the same authorization server-side
- Bootstrap 4 modal on `assemblyproject.html` and `sequencing.html`; URL built via `{% url ... pk=0 %}` with JS `/0/` → `/<pk>/` swap
- Management menu: added "Sequencing" → `/sequencing/` and "Assembly" → `/projects/`

**Bugs fixed along the way (worth remembering):**
1. **Modal didn't open via `$('#x').modal('show')`.** `base.html` loads slim jQuery + Bootstrap at the top, then reloads jQuery 3 more times near the bottom (admin vendor jQuery, jQuery 3.5.1, jQuery UI). Bootstrap's modal plugin was registered on the original `$`; by click time `$` is a fresh jQuery with no `.modal()`. **Fix:** add a hidden `<button data-toggle="modal" data-target="#x">` and trigger it with native `.click()` — Bootstrap's `[data-toggle="modal"]` event delegation on `document` (registered at Bootstrap load time) still catches the bubbling DOM event regardless of what `$` now points to.
2. **Edit button not showing for team members.** `UserProfile.user` is a `ForeignKey` (not OneToOne) with `related_name='user_profile'`, so `request.user.userprofile` raised `AttributeError`. The broad `except Exception: pass` silently swallowed it, leaving the editable set empty. **Fix:** replaced `members=profile` with `members__user=self.user`, which traverses the M2M directly to the User and avoids the multi-profile complication entirely. Same change applied to both tables and both POST views.
3. **`is_staff` bypass was too broad.** Most internal users have `is_staff=True`, so they all hit the "edit all" path. **Fix:** only `is_superuser` bypasses team-membership checks now.
4. **Pre-existing bug surfaced:** `SequencingTable.recipe` template column had `empty_values=()` so it tried to render `record.recipe.pk` even when `recipe` was None, raising `NoReverseMatch`. **Fix:** wrap the link in `{% if record.recipe %}`.

### Phase 3 — Role-based Dashboard ✅ COMPLETE

**Goal:** "My work" landing page that surfaces items needing the user's attention, scoped to their roles/teams.
**Non-goals:** new permissions (Phase 3 only queries Phase 1–2 state); reporting/analytics; background notifications.

#### Decisions (resolved open questions)
- **Pending-invite tracking:** `EARAssignmentInvite` model (migrations 0006+0007). Created alongside every `notify_assignment()` call; existing assignments backfilled as `accepted`. Signed-token email flow unchanged.
- **"Stuck EAR" threshold:** `EAR_STUCK_THRESHOLD_DAYS = 7` in `settings_dev.py`.
- **Post-login redirect:** `LOGIN_REDIRECT_URL = '/cbp-dev/dashboard/'` in `settings_dev.py`. Signup chain still routes to `/edit_profile/` via `ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL`.
- **Layout:** cards hide when empty; users with nothing to do see a placeholder.

#### What shipped
- `EARAssignmentInvite` model: `review`, `user`, `role` (reviewer/supervisor), `status` (pending/accepted/declined), `created_at`, `responded_at`. `unique_together = (review, user, role)`.
- `create_or_refresh_invite()` + `mark_invite_responded()` in `ear_review.py`.
- `dashboard_invite_response` view (`POST /dashboard/invite/<pk>/`) handles inline accept/decline with reassignment on decline.
- `DashboardView` at `/dashboard/` with six role-based cards (all in `views.py` context, no separate `dashboard.py`).
- `dashboard_action_count` context processor in `status/context_processors.py` — 3 COUNT queries, skipped for anonymous users, registered in `settings.py`.
- Nav "Dashboard" link with red badge in `base.html`.
- Species detail: `active_ear` + `ear_action` in context; pill shows invite pending / awaiting your review / awaiting your decision.
- Submitter/supervisor/reviewer exclusion: `select_supervisor` excludes assigned reviewers; `select_reviewer` excludes supervisor.

#### Key traversal paths (verified)
- Assembly team membership: `species__gt_rel__assembly_team__members__user`
- Sequencing team membership: `species__gt_rel__sequencing_team__members__user`
- (`gt_rel` is `GenomeTeam.species` related_name)

### Phase 4 — UI: consistent status pills ✅ SHIPPED (lightweight version)

**Goal (delivered):** unify the visual treatment of status indicators across the site, and make GOAT-derived labels readable.

**What shipped (instead of the template-tag/registry approach originally sketched):**
- `static/status.css`: merged `.status` and `.ear-status` into a single base rule with a fixed `width: 170px` and `box-sizing: border-box`, so every pill across the overview, dashboard, and EAR pages renders at the same width (sized for "Approved by reviewer", the longest label).
- New GOAT statuses `publication_available` and `insdc_submitted` added to the dark-green (Level 5) class.
- `OverviewTable.render_goat_sequencing_status` uses a `GOAT_LABEL_OVERRIDES` map: `publication_available → "published"`, `insdc_submitted → "insdc_sub"`. CSS class still uses the raw value, so styling is independent of the displayed label.
- Dashboard tables use the same `.status` / `.ear-status` classes inline.

**Not done (deferred — only worth doing if more divergence appears):** the dedicated `{% status_pill %}` template tag + central registry. Today the consistency comes from one shared CSS rule plus a small render override, which is enough for current needs.

### Phase 5 — Dashboard polish & per-project toggles ✅ SHIPPED

**Dashboard (`status/templates/dashboard.html` + `DashboardView`):**
- Species column links now point to the assembly project list (`?project=<pk>`) or sequencing list (`?species=<pk>`) instead of the broken `species_detail` URL (which is registered twice in `urls.py` — the second pattern with a literal `?` in the path wins under `reverse()` and produced bad URLs).
- A small "EAR" pill button next to the species name preserves quick access to the EAR review for EAR-related cards.
- Pencil-icon edit modals for **My assembly projects** and **My sequencing tasks**, mirroring `assemblyproject.html` / `sequencing.html`. POST handlers (`assembly_project_edit`, `sequencing_edit`) redirect back to the assembly/sequencing list — they don't yet preserve a `next=dashboard` redirect.
- `DashboardView.get_context_data` now passes `assembly_status_choices`, `sequencing_status_choices`, and `sequencing_status_fields` so the embedded modals render.

**Customization toggle for COPO (migration 0008):**
- New `Customization.show_copo` (`BooleanField(default=True)`). When unchecked from the admin, the `copo_status` table column AND the `copo_status` filter sidebar entry both disappear from: Overview, Species, Collection, and Samples pages.
- Implemented via `_copo_hidden()` + `_drop_copo_filter()` helpers in `views.py`, plus `get_table_kwargs` / `get_filterset` overrides on the four list views. CBP toggles it off; ERGA leaves it on.

**Pre-existing bug fixed in passing:** `TargetSpeciesTable.render_task` and `render_country` crashed with `TypeError: sequence item 0: expected str instance, NoneType found` when a `SampleCollection.task`/`country` had a null `short_name`/`name`. Added a guard in the set comprehensions.

---

## Key Decisions Made

- **Multiple reviewers**: M2M (not single FK) — supervisor can add reviewers
- **Roles**: Django Groups (`ear_reviewer`, `ear_supervisor`), not UserProfile roles field
- **Discussion thread**: flat with optional `parent` FK; open to all logged-in users to view, only participants can post
- **Reviewer assignment**: score-based algorithm (adapted from GitHub bot) with supervisor override
- **Research group**: separate `ResearchGroup` model with FK on `UserProfile` (not Affiliation — that's for publishing credits)
- **User ↔ team link**: `User` → `UserProfile` → team models → `GenomeTeam`. `Person` model is separate (non-user project contacts)
- **Build approach**: step by step, user tests each piece before proceeding; use `mariadb` not `mysql`

