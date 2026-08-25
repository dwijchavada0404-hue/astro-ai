# AstroAI deployment V1

AstroAI ships as a provider-neutral Docker image. The production ASGI entrypoint is `app.asgi:app` and the container listens on `$PORT` (default `8000`).

## Build and smoke test

```bash
docker build -t astroai .
docker run --rm -p 8000:8000 \
  -e ASTROAI_ENVIRONMENT=staging \
  -e ASTROAI_DOCS_ENABLED=true \
  -e ASTROAI_TRUSTED_HOSTS=localhost,127.0.0.1 \
  -e ASTROAI_PROFILE_DATABASE_PATH=/data/astroai_profiles.db \
  astroai
```

Then call `GET /health` and expect HTTP 200.

For a local production-like stack, run `docker compose up --build`.

## Production requirements

Set these environment variables explicitly in the hosting platform:

- `ASTROAI_ENVIRONMENT=production`
- `ASTROAI_DOCS_ENABLED=false`
- `ASTROAI_SECURITY_HEADERS_ENABLED=true`
- `ASTROAI_TRUSTED_HOSTS=<api-hostname>,127.0.0.1,localhost`
- `ASTROAI_CORS_ORIGINS=<frontend-origin>`
- `ASTROAI_PROFILE_DATABASE_PATH=/data/astroai_profiles.db`
- `ASTROAI_AUTH_ENABLED=true`
- `ASTROAI_API_AUTH_REQUIRED=true`
- `ASTROAI_AUTH_JWT_SECRET=<random secret of at least 32 characters>`
- `ASTROAI_AUTH_JWKS_URL=` (or an HTTPS JWKS endpoint for managed OIDC)
- `ASTROAI_AUTH_JWT_ISSUER=<configured issuer>`
- `ASTROAI_AUTH_JWT_AUDIENCE=<configured audience>`

Never commit production JWT secrets or a populated `.env` file.

For a managed OIDC provider, leave `ASTROAI_AUTH_JWT_SECRET` empty, set
`ASTROAI_AUTH_JWKS_URL` to the provider's HTTPS JWKS endpoint, and select the
provider's asymmetric `ASTROAI_AUTH_JWT_ALGORITHM` (normally `RS256`). Issuer
and audience validation remains mandatory. Existing HS256 deployments remain
supported for backwards compatibility.

## Persistent storage

The V1 profile and conversation repositories use SQLite. Production must mount durable storage at `/data` (or set `ASTROAI_PROFILE_DATABASE_PATH` to another persistent mount). An ephemeral container filesystem will lose users, birth profiles, and conversation history when the instance is replaced.

Run only **one application replica** while SQLite is the persistence backend. Horizontal scaling should wait until the repository layer is migrated to a shared database such as PostgreSQL.

## Reverse proxy / TLS

Terminate HTTPS at the hosting provider or reverse proxy. The container starts Uvicorn with proxy-header support. Restrict inbound traffic through the hosting platform and expose only the application port.

## Release checks

Before promoting a release:

1. GitHub Actions tests are green.
2. The Docker image builds successfully.
3. `/health` returns 200 from the deployed container.
4. Authentication is enabled in production.
5. The frontend origin and API hostname are explicit; wildcards are not used.
6. `/data` is a persistent volume and has a backup strategy.
7. API documentation is disabled in production.

## Current V1 limitation

SQLite is suitable for the initial single-instance beta. Before multi-instance/high-availability deployment, migrate persistent repositories to a shared production database.
