#!/usr/bin/env bash
set -euo pipefail

frontend_url="${ASTROAI_FRONTEND_URL:-https://powerful-exploration-production-9475.up.railway.app}"
api_url="${ASTROAI_API_URL:-https://astro-ai-production-54a7.up.railway.app}"
smoke_dir="$(mktemp -d)"
trap 'rm -rf -- "$smoke_dir"' EXIT

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
  --output "$smoke_dir/readiness.json" \
  "$api_url/readyz"
grep -q '"profile_database"[[:space:]]*:[[:space:]]*"ok"' "$smoke_dir/readiness.json"

auth_status="$(curl --silent --show-error --output "$smoke_dir/auth.json" --write-out '%{http_code}' "$api_url/api/v1/auth/me")"
test "$auth_status" = "401"
grep -qi 'bearer authentication is required' "$smoke_dir/auth.json"

echo "AstroAI staging smoke checks passed."
