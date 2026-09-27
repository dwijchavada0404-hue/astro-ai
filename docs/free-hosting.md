# AstroAI free-hosting migration

## Target architecture
- API: Render Free Web Service
- Frontend: Cloudflare Pages Free
- Database: Neon Free PostgreSQL
- Authentication: existing Auth0 tenant
- Source: GitHub main

AstroAI already supports PostgreSQL through ASTROAI_DATABASE_URL. The storage layer accepts PostgreSQL URLs and translates the repository's SQLite-style parameter placeholders for psycopg. Production settings already require PostgreSQL or an absolute SQLite path under /data.

Use Neon rather than Render's free PostgreSQL for this migration because Render's current free PostgreSQL instances expire after 30 days. Neon currently offers a free PostgreSQL plan with 0.5 GB storage per project and scale-to-zero compute.

## Render API
Create the repository as a Web Service from GitHub:
- Root directory: repository root
- Runtime: Docker
- Dockerfile: Dockerfile
- Branch: main
- Health check: /readyz
- Auto deploy: enabled
- Plan: Free

The included render.yaml is a blueprint starting point. Sensitive values intentionally use sync: false; enter them in the Render dashboard.

Required production environment variables:
- ASTROAI_ENVIRONMENT=production
- ASTROAI_DOCS_ENABLED=false
- ASTROAI_API_AUTH_REQUIRED=true
- ASTROAI_AUTH_ENABLED=true
- ASTROAI_AUTH_JWT_ALGORITHM=RS256
- ASTROAI_AUTH_JWKS_URL=<Auth0 JWKS URL>
- ASTROAI_AUTH_JWT_ISSUER=<Auth0 issuer URL>
- ASTROAI_AUTH_JWT_AUDIENCE=<Auth0 API audience>
- ASTROAI_DATABASE_URL=<Neon connection string>
- ASTROAI_CORS_ORIGINS=<Cloudflare Pages production URL>
- ASTROAI_TRUSTED_HOSTS=<Render API hostname>
- ASTROAI_GEOCODING_PROVIDER=<configured keyed provider>
- ASTROAI_GEOCODING_API_KEY=<provider key>

Do not commit these secrets.

## Cloudflare Pages frontend
Create a Pages project from the same GitHub repository:
- Production branch: main
- Root directory: web
- Build command: npm ci && npm run build
- Output directory: dist

Build environment variables:
- VITE_ASTROAI_ENVIRONMENT=production
- VITE_ASTROAI_API_URL=<Render API URL>
- VITE_OIDC_AUTHORITY=<Auth0 issuer URL>
- VITE_OIDC_CLIENT_ID=<Auth0 SPA client ID>
- VITE_OIDC_AUDIENCE=<Auth0 API audience>
- VITE_OIDC_SCOPE=openid profile email

Update the Auth0 application allowed callback/logout/web-origin settings to the final Cloudflare Pages URL.

## Database migration
Preserve any existing profile/conversation data that must be retained before switching traffic. The existing Railway volume may be inaccessible while the trial is expired, so do not assume the SQLite database can be exported.

If existing data is not required, start with an empty Neon database; AstroAI initializes its schema on startup.

## Validation
1. GET /livez returns HTTP 200.
2. GET /readyz returns HTTP 200 and reports profile_database: ok.
3. Authenticated API calls succeed.
4. Create/list/update/delete a birth profile.
5. Create/list a conversation and messages.
6. Verify answer_language reaches the top-level question API.
7. Verify frontend Auth0 login and logout.
8. Verify representative chart/question UAT.
9. Confirm no frontend runtime reference points at Railway.

## Rollback
Keep the Railway project untouched until the replacement passes UAT. Do not delete the existing Railway services or volume during migration.