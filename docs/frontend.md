# AstroAI frontend


The first web client lives in `web/`. It is a React and TypeScript single-page
application that uses OIDC Authorization Code with PKCE. The browser receives
only short-lived provider access tokens; AstroAI's JWT signing secret is never
included in frontend code.


## Local development


```bash
cd web
cp .env.example .env.local
npm ci
npm run dev
```


The example API URL points to Railway staging. Configure a real OIDC authority,
public SPA client ID, allowed callback URL (`http://localhost:5173/auth/callback`),
logout URL (`http://localhost:5173`), audience, and matching CORS origin before
testing sign-in.


## Production configuration


- `VITE_ASTROAI_API_URL`: deployed AstroAI API origin
- `VITE_OIDC_AUTHORITY`: managed identity-provider issuer/authority
- `VITE_OIDC_CLIENT_ID`: public SPA client identifier
- `VITE_OIDC_SCOPE`: normally `openid profile email`
- `VITE_OIDC_AUDIENCE`: API audience expected by AstroAI


OIDC provider secrets are not used by this SPA. The API validates the access
token against the provider JWKS endpoint, issuer, audience and algorithm.
The client observes both the token expiry timestamp and OIDC provider session
events. Expired sessions return to sign-in with a clear message; saved profiles
and conversations remain server-side and are not removed.

Authenticated users can permanently delete their AstroAI application data from
the Birth profiles screen after typing an explicit confirmation. This removes
their conversations, messages, saved birth profiles and AstroAI user metadata,
then signs them out. The external OIDC identity remains managed by the identity
provider and is outside AstroAI's application database.


## Railway hosting


Deploy `web/` as a separate Railway service. Its Dockerfile builds the static
React application and serves it on port `8080`; use `/health` as its Railway
healthcheck. The staging API origin is the built-in fallback, while
`VITE_ASTROAI_API_URL` can override it at build time for another environment.


After Railway generates the public frontend domain, add that exact origin to
the backend's `ASTROAI_CORS_ORIGINS` setting before enabling OIDC sign-in.


For Docker/Railway builds, pass the public `VITE_*` values as Docker build
arguments as well as service variables. Vite reads them while producing the
static bundle; runtime-only environment variables cannot change an already
built browser application. These values are intentionally public configuration,
not provider secrets.
