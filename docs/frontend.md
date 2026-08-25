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
