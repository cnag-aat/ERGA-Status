# ERGA GTC — ear-review branch

Django 3.2.25 + MariaDB app for tracking genome sequencing projects. Adds an EAR (ERGA Assembly Report) review workflow.

Active feature briefs: `EAR_REVIEW_BRIEF.md` (core EAR review), `REPLACE_PDF_BRIEF.md` (replace-EAR-PDF mid-review).

## Environment

| Item | Value |
|------|-------|
| Project dir | `/home/www/resistome.cnag.cat/ear-review/` |
| Dev DB | `cbp_dev` (MariaDB) |
| Dev settings | `erga/settings_dev.py` |
| Dev URL | `https://genomes.cnag.cat/cbp-dev` |
| venv | `/home/www/resistome.cnag.cat/virtualenvs/incredble_venv` |
| Reload | `touch erga/wsgi.py` |
| Log | `~/logs/ear-review-dev.log` |
| Static | `/home/www/resistome.cnag.cat/incredible/deployment/static/` |

```bash
source /home/www/resistome.cnag.cat/virtualenvs/incredble_venv/bin/activate
python manage.py check --settings=erga.settings_dev
python manage.py makemigrations --settings=erga.settings_dev
python manage.py migrate --settings=erga.settings_dev
python manage.py collectstatic --settings=erga.settings_dev --noinput
```

## Working rules

- Change files only inside `ear-review/` unless explicitly authorized
- Use `mariadb` not `mysql` for DB commands; DB password has special chars — use `~/.mydev.cnf` (chmod 600)
- Step-by-step: user tests each piece before proceeding
- `LOGIN_URL = '/cbp-dev/accounts/login/'` (dev settings); `LOGIN_REDIRECT_URL = '/cbp-dev/dashboard/'`
- `is_superuser` (not `is_staff`) is the correct check for "edit everything" — most internal users have `is_staff=True`

## Stack

- Auth: django-allauth (mandatory email verification)
- Tables: django-tables2 + django-filters
- Forms: django-addanother (`AddAnotherWidgetWrapper` popups)
- File uploads: up to 500 MB; Apache `LimitRequestBody 524288000`, `SecRequestBodyLimit 524288000`; ModSecurity blocks large uploads — exempt `/cbp-dev/ear/` paths in Apache config
- Email: `settings.DEFAULT_FROM_EMAIL`, `fail_silently=True`
- Customization: `Customization` singleton model in admin — `show_copo` toggles COPO columns/filters site-wide

## Key files

| File | Purpose |
|------|---------|
| `status/models.py` | All models + signals |
| `status/ear_review.py` | EAR business logic: reviewer selection, notifications, signed tokens |
| `status/views.py` | All views (EAR views appended at bottom) |
| `status/tables.py` | django-tables2 table classes |
| `status/filters.py` | django-filters filtersets |
| `status/urls.py` | URL patterns |
| `status/templates/` | Templates |
| `status/admin.py` | Admin — `EARReviewAdmin.save_related` triggers `auto_assign_reviewer` |
| `status/context_processors.py` | `dashboard_action_count` — 3 COUNT queries, skipped for anon users |
| `erga/settings_dev.py` | Dev overrides incl. `EAR_STUCK_THRESHOLD_DAYS = 7` |

## Data model

### Core species → assembly chain

```
TargetSpecies ──OneToOne──► AssemblyProject (related_name='assembly_rel')
                                │
                                ├──OneToOne──► EARReview (related_name='ear_review')
                                │
                                └──FK (many)──► Assembly
                                                  type: Primary / Hap1 / Hap2 / Alternate / MT / Chloroplast / Endosymbiont
                                                  chromosome_level (NullBooleanField)
                                                  span, contig_n50, scaffold_n50 (bp integers)
                                                  busco, busco_db, busco_version, qv
                                                  accession (ENA Study), gca
                                                  pipeline ──FK──► AssemblyPipeline
```

### Team → species chain

```
GenomeTeam.species ──FK──► TargetSpecies          (related_name: gt_rel)
GenomeTeam.assembly_team ──FK──► AssemblyTeam
AssemblyTeam.members ──M2M──► UserProfile
UserProfile.user ──FK──► User                     (NOT OneToOne — use members__user=user)
UserProfile.research_group ──FK──► ResearchGroup  (COI check for EAR reviewer selection)
UserProfile.calling_score IntegerField default 1000
```

### EAR models

```
EARReview
  assembly_project  OneToOne → AssemblyProject
  submitted_by      FK → User
  supervisor        FK → User (nullable)
  reviewers         M2M → User via EARReviewer (through_fields required)
  ear_pdf           FileField  media/ear_pdfs/   (permanent)
  pretext_file      FileField  media/pretext/    (nullable; deleted on acceptance via post_save signal)
  status            submitted → in_review → reviewer_approved → accepted
                                         ↘ rejected            ↘ declined
  created_at, updated_at

EARReviewer (through model)
  review, reviewer, added_by, added_at

EARComment
  review, author, body, parent (self FK nullable), created_at

EARAttachment
  comment, file (media/ear_attachments/), uploaded_at

EARAssignmentInvite
  review, user, role ('reviewer'|'supervisor'), status ('pending'|'accepted'|'declined')
  created_at, responded_at
  unique_together = (review, user, role)
```

### Django groups

- `ear_reviewer` — eligible to be assigned as reviewer
- `ear_supervisor` — eligible to be assigned as supervisor
- Submitter = any user in an AssemblyTeam (no group needed)
- Submitter, supervisor, and reviewer(s) must all be distinct

### AssemblyProject → EARReview status sync

`EAR_TO_ASSEMBLY_STATUS`: submitted/in_review → `UnderReview`; reviewer_approved/accepted → `Approved`; rejected/declined → `UnderReview`

## Key traversal paths

```python
# Assembly team members for a species
species__gt_rel__assembly_team__members__user

# Sequencing team members for a species
species__gt_rel__sequencing_team__members__user

# User's editable species via AssemblyTeam
AssemblyTeam.objects.filter(members__user=user).values_list('genometeam__species_id', flat=True)

# EAR for an assembly
assembly.project.ear_review  # may raise RelatedObjectDoesNotExist — use getattr(..., None)
```

## Gotchas

1. **`UserProfile.user` is FK, not OneToOne.** `request.user.userprofile` raises `AttributeError`. Always traverse via `members__user=user` or `UserProfile.objects.get(user=user)`.

2. **`gt_rel` is `GenomeTeam.species` `related_name`.** The path `species__gt_rel__assembly_team` is the only correct way to reach teams from a species.

3. **jQuery modal conflict in `base.html`.** `base.html` loads jQuery multiple times (admin vendor + jQuery 3.5.1 + jQuery UI), overwriting `$` after Bootstrap registers its modal plugin. `$('#modal').modal('show')` silently fails. Fix: add a hidden `<button data-toggle="modal" data-target="#modal">` and trigger it with native `.click()` — Bootstrap's delegated `[data-toggle="modal"]` handler (registered at load time on `document`) catches the bubbled event regardless of `$`.

4. **`urls.py` has fake query-string patterns** like `path("species/?scientific_name=<scientific_name>", ...)`. Django path() never matches query strings; these patterns are dead. Real filtering is done in `get_queryset` via `self.request.GET`. Don't add more of these.

5. **`EARReviewer` through model requires `through_fields`.** Omitting it causes Django to complain about ambiguous FK when there are multiple FKs to the same model.

6. **Pretext file is nullable at model level** (not enforced by `blank=False`) so post-acceptance deletion doesn't break validation. Required-on-creation is enforced at the form level only.

7. **`AssemblyListView` global queryset** filters for chromosome-level primaries only (`chromosome_level=True`, excludes Hap2/Alternate/MT/Chloroplast/Endosymbiont). When `?project=<pk>` is passed, all assembly types for that project are returned instead.

8. **`tables.py render_task` returns None → site crash.** Two `render_task` methods in `status/tables.py` can return/produce `None`, causing `TypeError: sequence item 0: expected str instance, NoneType found` on any page that renders those tables (species list, sample collection). Always filter None defensively: `';'.join(t for t in tasks if t is not None)` and always return `''` as a fallback instead of falling off the end of the method.

9. **`populate() isn't reentrant` — restart Apache, not just wsgi.py.** When the mod_wsgi daemon starts, its 15 default threads race to execute `wsgi.py` concurrently, two of them calling `django.setup()` simultaneously. The second call raises `RuntimeError: populate() isn't reentrant`, leaving the daemon process permanently broken (same PID fails on every subsequent request — visible in `~/logs/server.error.log`). `touch erga/wsgi.py` alone does NOT fix this because it only schedules a reload; the stuck process keeps serving (and failing) requests. **Fix: `sudo systemctl restart httpd`** — this kills the stuck process and starts fresh. To prevent recurrence, `WSGIDaemonProcess cbp-dev-site` in the Apache config should have `threads=1` added (safe for dev).

10. **`ACCOUNT_UNIQUE_EMAIL` must stay `True`.** allauth asserts `(AUTHENTICATION_METHOD == 'username') or UNIQUE_EMAIL` at startup. Setting `ACCOUNT_UNIQUE_EMAIL = False` while using `ACCOUNT_AUTHENTICATION_METHOD = 'username_email'` kills the entire site with an `AssertionError`. To allow no-email test users, set only `ACCOUNT_EMAIL_REQUIRED = False` and `ACCOUNT_EMAIL_VERIFICATION = none` in the dev `.env` — multiple users can share an empty email without needing `UNIQUE_EMAIL = False`.

11. **`erga/settings.py` and `cbp/erga/settings.py` must be kept in sync.** After editing `ear-review/erga/settings.py`, copy it to `cbp/erga/settings.py`: `cp ear-review/erga/settings.py cbp/erga/settings.py`. They are identical files — any divergence causes confusing environment differences.
