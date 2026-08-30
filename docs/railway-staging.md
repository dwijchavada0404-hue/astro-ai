# Railway staging deployment

Railway is AstroAI's selected provider for the private staging phase. It can deploy the repository's Dockerfile, injects the `PORT` environment variable consumed by the existing container command, and supports a persistent mounted volume for the current SQLite-backed profile and conversation stores.

## Create the staging service

1. Create a Railway project and a `staging` environment.
2. Deploy the GitHub repository `dwijchavada0404-hue/astro-ai` from `main`.
3. Railway detects `railway.toml` and builds the root `Dockerfile`.
4. Add a persistent Railway Volume mounted at `/data`.
5. Keep **exactly one replica**. The current SQLite store must not be scaled horizontally.
6. Configure the service healthcheck as `/health` (also defined in `railway.toml`).
7. Enable volume backups before storing any real user data.

## Required service variables

Set the following in Railway's service Variables UI. Do not commit these values.

```text
ASTROAI_ENVIRONMENT=staging
ASTROAI_DOCS_ENABLED=false
ASTROAI_SECURITY_HEADERS_ENABLED=true
ASTROAI_RATE_LIMIT_ENABLED=true
ASTROAI_RATE_LIMIT_REQUESTS_PER_MINUTE=120
ASTROAI_PROFILE_DATABASE_PATH=/data/astroai_profiles.db
ASTROAI_AUTH_ENABLED=true
ASTROAI_API_AUTH_REQUIRED=true
ASTROAI_AUTH_JWT_SECRET=<random secret with at least 32 characters>
ASTROAI_AUTH_JWT_ISSUER=<staging issuer>
ASTROAI_AUTH_JWT_AUDIENCE=<staging audience>
ASTROAI_CORS_ORIGINS=<explicit staging frontend origin>
ASTROAI_TRUSTED_HOSTS=<railway-generated-domain>,healthcheck.railway.app
```

Railway healthchecks use the `healthcheck.railway.app` host, so it must be included in `ASTROAI_TRUSTED_HOSTS`. After generating a Railway domain, replace `<railway-generated-domain>` with that exact hostname. Do not use wildcard CORS or trusted hosts.

## Smoke test

After Railway reports a successful deployment, verify:

```bash
curl --fail --silent --show-error https://<railway-generated-domain>/health
```

The expected response is HTTP 200 with `status: "ok"`. Confirm the service's deployment logs show the Uvicorn server listening on Railway's injected `PORT`.

## Current staging boundary

A generated Railway domain is internet reachable. The staging configuration must therefore set `ASTROAI_API_AUTH_REQUIRED=true`, which requires a valid bearer token for every `/api/*` route while leaving `/health`, `/livez`, and `/readyz` available to deployment infrastructure. Development remains backwards-compatible because the setting defaults to `false` outside deployed environments.

The rate limit applies to authenticated `/api/*` requests per user. It does not
count `/health`, `/livez`, `/readyz`, or browser preflight requests.

## Operational constraints

- A volume-backed Railway deployment has a brief replacement gap during redeploy; Railway prevents simultaneous volume mounts to avoid SQLite corruption.
- The mounted volume is required for every deploy; the container filesystem is ephemeral.
- Keep data backups outside the running service and verify restoration before using real accounts.
- Move persistence to PostgreSQL before multi-replica or high-availability deployment.
