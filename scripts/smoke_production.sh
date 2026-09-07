#!/usr/bin/env bash
set -euo pipefail

: "${ASTROAI_PRODUCTION_FRONTEND_URL:?ASTROAI_PRODUCTION_FRONTEND_URL is required}"
: "${ASTROAI_PRODUCTION_API_URL:?ASTROAI_PRODUCTION_API_URL is required}"

frontend_url="${ASTROAI_PRODUCTION_FRONTEND_URL%/}"
api_url="${ASTROAI_PRODUCTION_API_URL%/}"
smoke_dir="$(mktemp -d)"
trap 'rm -rf -- "$smoke_dir"' EXIT

case "$frontend_url" in
  https://*) ;;
  *) echo "Production frontend URL must use HTTPS." >&2; exit 1 ;;
esac
case "$api_url" in
  https://*) ;;
  *) echo "Production API URL must use HTTPS." >&2; exit 1 ;;
esac

if printf '%s\n%s\n' "$frontend_url" "$api_url" | grep -Eqi 'localhost|127\.0\.0\.1'; then
  echo "Production smoke URLs must not point to localhost." >&2
  exit 1
fi

curl --fail --silent --show-error --location \
  --dump-header "$smoke_dir/frontend.headers" \
  --output "$smoke_dir/frontend.html" \
  "$frontend_url/"
grep -Eiq '^content-security-policy:.*default-src' "$smoke_dir/frontend.headers"

curl --fail --silent --show-error \
  --output "$smoke_dir/frontend-health.txt" \
  "$frontend_url/health"
grep -qx 'ok' "$smoke_dir/frontend-health.txt"

curl --fail --silent --show-error \
  --output "$smoke_dir/security.txt" \
  "$frontend_url/.well-known/security.txt"
grep -q '^Contact: https://' "$smoke_dir/security.txt"

curl --fail --silent --show-error \
  --output "$smoke_dir/api-health.json" \
  "$api_url/health"
grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' "$smoke_dir/api-health.json"

curl --fail --silent --show-error \
  --output "$smoke_dir/liveness.json" \
  "$api_url/livez"
grep -q '"status"[[:space:]]*:[[:space:]]*"ok"' "$smoke_dir/liveness.json"

curl --fail --silent --show-error \
  --output "$smoke_dir/readiness.json" \
  "$api_url/readyz"
grep -q '"status"[[:space:]]*:[[:space:]]*"ready"' "$smoke_dir/readiness.json"
grep -q '"environment"[[:space:]]*:[[:space:]]*"production"' "$smoke_dir/readiness.json"
grep -q '"profile_database"[[:space:]]*:[[:space:]]*"ok"' "$smoke_dir/readiness.json"

auth_status="$(curl --silent --show-error --output "$smoke_dir/auth.json" --write-out '%{http_code}' "$api_url/api/v1/auth/me")"
test "$auth_status" = "401"
grep -qi 'bearer authentication is required' "$smoke_dir/auth.json"

cors_headers="$smoke_dir/cors.headers"
curl --silent --show-error --output /dev/null --dump-header "$cors_headers" \
  -X OPTIONS "$api_url/api/v1/auth/me" \
  -H "Origin: $frontend_url" \
  -H 'Access-Control-Request-Method: GET'
grep -Fqi "access-control-allow-origin: $frontend_url" "$cors_headers"

echo "AstroAI production smoke checks passed."
