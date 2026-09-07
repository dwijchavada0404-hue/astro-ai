# AstroAI production launch gate

AstroAI's public production environment must not use the community `nominatim.openstreetmap.org` service for birth-place lookup.

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

## Launch sequence

Before switching the Railway API service to `ASTROAI_ENVIRONMENT=production`:

1. Create the production provider account/key.
2. Add the four geocoding variables above to the production API service.
3. Configure production Auth/OIDC, CORS and trusted hosts.
4. Keep `/readyz` as the Railway health gate.
5. Run the standard staging smoke equivalent against the production frontend/API before announcing the public beta.
