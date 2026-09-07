# AstroAI production launch gate

AstroAI's public production environment must not use the community `nominatim.openstreetmap.org` service for birth-place lookup and must not store SQLite data on an ephemeral container filesystem.

## Production geocoding

The runtime supports two geocoding modes:

- `nominatim` — development/staging compatibility only.
- `openmapquest` — keyed commercial Nominatim-compatible provider intended for production.

Production startup validation rejects `ASTROAI_GEOCODING_PROVIDER=nominatim`. A production service must configure:

```text
ASTROAI_GEOCODING_PROVIDER=openmapquest
ASTROAI_GEOCODING_API_KEY=<provider API key>
ASTROAI_GEOCODING_TIMEOUT_SECONDS=10
ASTROAI_GEOCODING_USER_AGENT=astro-ai/1.0
```

The API key is a server-side secret and must be configured in Railway Variables; never expose it through `VITE_*` frontend variables or commit it to the repository.

Resolved places remain cached in-process for repeated identical normalized queries. The timezone continues to be derived locally with `timezonefinder`, so the geocoding provider is used only to resolve the place to latitude/longitude and a display address.

Provider failures are converted to AstroAI's existing generic temporary-unavailability error and do not expose provider credentials or raw upstream error details to users.

## Production persistence

AstroAI supports PostgreSQL or SQLite. If production continues on SQLite for the public beta, the runtime now requires an absolute database file path under the mounted Railway volume:

```text
ASTROAI_PROFILE_DATABASE_PATH=/data/astroai_profiles.db
```

A relative path such as `data/astroai_profiles.db` or an absolute path outside `/data` is rejected at startup when `ASTROAI_ENVIRONMENT=production`. This prevents a production deployment from silently writing user data to Railway's ephemeral container filesystem.

PostgreSQL deployments using `ASTROAI_DATABASE_URL=postgresql://...` are not subject to the `/data` path rule.

`/readyz` verifies that the configured store can be queried. For SQLite it additionally runs `PRAGMA quick_check`; a corrupt or unreadable file therefore makes readiness fail with HTTP 503 rather than allowing Railway to mark the service healthy.

## Backup and restore verification

Railway volume backups remain the primary infrastructure backup for a SQLite public beta. Enable them before real production accounts are created.

AstroAI also includes `scripts/sqlite_recovery.py` for operator-controlled consistency checks and offline backup drills. The backup command uses SQLite's online backup API, which safely copies a live WAL-backed database into a standalone backup file and verifies it before reporting success:

```bash
python scripts/sqlite_recovery.py backup /data/astroai_profiles.db /data/backups/astroai-YYYYMMDD.db
python scripts/sqlite_recovery.py verify /data/backups/astroai-YYYYMMDD.db
```

Verification requires `PRAGMA quick_check=ok` and confirms the core AstroAI tables `user_profiles`, `birth_profiles`, `conversations`, and `messages` are present. A failed verification must block promotion of that backup as a recovery point.

Before launch, perform at least one restore drill by copying a verified backup to an isolated location and running the `verify` command against that restored copy. Do not overwrite the live database merely to test restoration.

## Launch sequence

Before switching the Railway API service to `ASTROAI_ENVIRONMENT=production`:

1. Create the production geocoding provider account/key and configure the four geocoding variables above.
2. Configure production Auth/OIDC, CORS and trusted hosts.
3. Keep exactly one API replica while production uses SQLite, and mount the Railway volume at `/data`.
4. Set `ASTROAI_PROFILE_DATABASE_PATH=/data/astroai_profiles.db` or move to PostgreSQL.
5. Enable Railway volume backups and complete one isolated restore-verification drill.
6. Keep `/readyz` as the Railway health gate.
7. Run the standard staging smoke equivalent against the production frontend/API before announcing the public beta.
