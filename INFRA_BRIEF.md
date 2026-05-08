# Infrastructure & Housekeeping — 2026-05-08

## Branch consolidation

`ear-review` and `generalized` had diverged from common ancestor `7b4feb8` with parallel (non-merged) commits for the same changes, making them unmergeable. Resolution:

- `ear-review` had a stray unmatched `{% endif %}` in `status/templates/index.html` — `generalized` was the correct one.
- The one unique commit on `ear-review` (`55c8edb` — remove deploy.sh) was already fully present on `generalized` (deploy.sh untracked, already in .gitignore). No cherry-pick needed.
- `ear-review` deleted locally and from `origin`. `generalized` is now the sole dev branch.

## Settings consolidation

`erga/settings_dev.py` was removed in a prior session. Settings are now a single `erga/settings.py` with all environment-specific values read from `erga/.env` (see `erga/.env.template`). CLAUDE.md updated accordingly.

## Static files — collectstatic fixed

CSS files were in project-root `static/` (flat), but templates reference `/static/css/<file>` and STATIC_ROOT is `incredible/deployment/static/`. Collectstatic wasn't picking them up (no `STATICFILES_DIRS` configured).

**Changes:**
- `git mv static/*.css static/css/` — files now match the URL paths templates expect.
- `erga/settings.py`: `STATIC_ROOT` and `STATICFILES_DIRS` now read from `.env`.
- New `.env` keys: `STATIC_ROOT`, `STATICFILES_SOURCE` (defaults to `<PROJECT_DIR>/static`).
- `.env.template` updated with both keys.

## Meadow Green palette

New pill colour palette added: lime-cream → light-green-2 → ocean-mist → bondi-blue → baltic-blue (`#d9ed92` → `#99d98c` → `#52b69a` → `#168aad` → `#1e6091`). Dark text on the two light stages; white on the rest. Red (`#D2042D`) kept for failures; gray (`#e9ecef`) for no-value.

**Changes:**
- `static/css/palette-meadow.css` created.
- `'meadow'` added to `PILL_PALETTE_CHOICES` in `status/models.py`.
- Meadow colors baked into `status.css` as the new default (replacing the old "original" greens).
- `'original'` removed from `PILL_PALETTE_CHOICES`; `base.html` condition simplified.
- DB `Customization` row updated to `pill_palette='meadow'`; model `default` set to `'meadow'`.

## Lost .env recovery

`erga/.env` was deleted by a prior Claude session. Restored by copying from `/home/www/resistome.cnag.cat/cbp/erga/.env` and adjusting dev-specific values (`DB_NAME=cbp_dev`, `ENABLE_CRONS=False`, `STATIC_ROOT`, `STATICFILES_SOURCE`). Permissions set to `644` (Apache-readable).

**Note:** `.env` must never be touched by branch operations — it is gitignored and irreplaceable without manual secret entry. File a Claude Code issue if destructive branch/cleanup commands affect gitignored files.
