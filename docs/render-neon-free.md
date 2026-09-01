# Card-free Render + Neon deployment

This guide deploys AstroAI without a credit card while keeping user profiles
and conversation history outside the web-service filesystem.

## Architecture and limitations

- Render Free hosts the API as a Docker web service and the web client as a
  static site.
- Neon Free supplies PostgreSQL through `ASTROAI_DATABASE_URL`.
- Auth0 remains the identity provider.
- Render Free web services spin down after 15 minutes with no traffic; the
  first request after sleep can take about one minute.
- Keep Railway active until both Render services and the Neon-backed API have
  passed the smoke checks. Do not copy or expose the Railway JWT secret.

## Create the Neon database

1. Create a Neon Free project and select a region close to the Render API.
2. Copy its pooled PostgreSQL connection URL with `sslmode=require`.
3. Store that value only as Render's `ASTROAI_DATABASE_URL` secret. Do not put
   it in GitHub, frontend settings, or a Vite variable.

AstroAI creates the required tables and indexes on first connection. The
existing Railway SQLite data is intentionally not copied automatically; this
prevents staging test data and user data from being moved without a reviewed
export and import.

## Create the Render API

Create a **Web Service** from `dwijchavada0404-hue/astro-ai`, branch `main`:

- Runtime: Docker
- Dockerfile path: `Dockerfile`
- Plan: Free
- Health check path: `/readyz`
- Auto deploy: enabled

Set the following environment variables. Values shown in angle brackets must be
replaced with the generated Render domains or existing Auth0 public values:

```text
ASTROAI_ENVIRONMENT=production
ASTROAI_DOCS_ENABLED=false
ASTROAI_SECURITY_HEADERS_ENABLED=true
ASTROAI_RATE_LIMIT_ENABLED=true
ASTROAI_RATE_LIMIT_REQUESTS_PER_MINUTE=120
ASTROAI_REQUEST_LOGGING_ENABLED=true
ASTROAI_SLOW_REQUEST_THRESHOLD_MS=2000
ASTROAI_DATABASE_URL=<Neon pooled URL with sslmode=require>
ASTROAI_AUTH_ENABLED=true
ASTROAI_API_AUTH_REQUIRED=true
ASTROAI_AUTH_JWKS_URL=https://dev-q0zcg4qyan6zsd8w.eu.auth0.com/.well-known/jwks.json
ASTROAI_AUTH_JWT_ALGORITHM=RS256
ASTROAI_AUTH_JWT_ISSUER=https://dev-q0zcg4qyan6zsd8w.eu.auth0.com/
ASTROAI_AUTH_JWT_AUDIENCE=<Render API public origin>
ASTROAI_TRUSTED_HOSTS=<Render API hostname>
ASTROAI_CORS_ORIGINS=<Render frontend origin>
```

`ASTROAI_AUTH_JWT_AUDIENCE` must equal the API identifier configured in Auth0.
If the existing Auth0 API identifier remains the Railway API URL, create a
separate Render audience/API registration before changing this value.

## Create the Render frontend

Create a **Static Site** from the same repository:

- Root directory: `web`
- Build command: `npm ci && npm run build`
- Publish directory: `dist`
- Auto deploy: enabled

Add these public build-time variables:

```text
VITE_ASTROAI_API_URL=<Render API public origin>
VITE_OIDC_AUTHORITY=https://dev-q0zcg4qyan6zsd8w.eu.auth0.com
VITE_OIDC_CLIENT_ID=1yVrXZbxjYuLVhC5s60uPmVzVlbzb0XS
VITE_OIDC_SCOPE=openid profile email
VITE_OIDC_AUDIENCE=<Render API audience>
```

## Update Auth0 after both Render URLs exist

Add the Render frontend origin to the Auth0 SPA application's allowed callback
URLs, allowed logout URLs, and allowed web origins. If the API audience changes,
create or update the Auth0 API registration, grant the SPA access, and use the
same audience in both the API and frontend variables.

## Cutover checklist

1. Render API `/health` and `/readyz` return HTTP 200.
2. The Render frontend reports the API online.
3. Auth0 sign-in returns to the Render frontend.
4. Create a new test profile, conversation, and message; refresh the page and
   confirm that they persist.
5. Only after this passes, decide whether to export/import Railway SQLite user
   data. Keep Railway until the data decision is completed.
