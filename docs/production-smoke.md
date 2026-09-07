# AstroAI production smoke gate

The public production environment has a dedicated manual GitHub Actions gate in `.github/workflows/production-smoke.yml`. It is intentionally not scheduled and does not run automatically after every main push. Run it when the production Railway frontend/API have been created or changed and before announcing a public release.

## Required GitHub repository variables

Configure these non-secret repository variables:

```text
ASTROAI_PRODUCTION_FRONTEND_URL=https://<production-frontend>
ASTROAI_PRODUCTION_API_URL=https://<production-api>
```

Do not put Auth0 secrets, JWT credentials, geocoding keys, database credentials, or any user token in this workflow. The production smoke is deliberately unauthenticated and verifies the public security boundary without reading customer data.

## Checks

`scripts/smoke_production.sh` verifies:

- frontend root loads over HTTPS;
- Content Security Policy is present;
- frontend `/health` returns `ok`;
- `/.well-known/security.txt` exposes an HTTPS security contact;
- API `/health` and `/livez` are healthy;
- API `/readyz` reports `status=ready`, `environment=production`, and `profile_database=ok`;
- an unauthenticated protected API request returns HTTP 401 with the bearer-authentication boundary intact;
- an OPTIONS request from the exact production frontend origin is allowed by API CORS;
- production URLs do not point to localhost.

## Launch use

After the real production Railway services and Auth0/OIDC application exist:

1. Set the two repository variables above.
2. Open GitHub Actions and run **Production smoke** manually.
3. Treat a red production smoke as a release blocker.
4. Only announce the public beta after the workflow is green and the human UAT journey has also passed.
