# Astro AI — Milestone 1

Copyright © 2026 Dwij Chavada.

AstroAI is free software licensed under the GNU Affero General Public License
version 3. You may use, modify and redistribute it under those terms, including
for commercial purposes. If you operate a modified version over a network, you
must offer its users the complete corresponding source code. See [LICENSE](LICENSE)
and [NOTICE](NOTICE).

A Vedic astrology calculation API that converts birth date, time, and place into structured chart JSON.

## Methodology

- Vedic / sidereal zodiac
- Lahiri ayanamsa
- Whole-sign houses
- Swiss Ephemeris via `pysweph`
- Mean lunar node for Rahu/Ketu
- Vimshottari dasha from Moon's nakshatra

> Astrology is a traditional interpretive system, not a scientifically validated method of predicting future events. This milestone only calculates chart data; it does not generate predictions.

## Requirements

- Python 3.11+ recommended
- Internet access for place lookup through OpenStreetMap Nominatim
- Compliance with the repository's AGPL-3.0 license and third-party notices.
  AstroAI uses the AGPL editions of `pysweph` and Swiss Ephemeris.

## Windows setup

```powershell
cd astro_ai_milestone1

py -3.11 -m venv .venv
.venv\Scripts\activate

python -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload
```

## macOS/Linux

```bash
cd astro_ai_milestone1

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn app.main:app --reload
```

API docs:
http://127.0.0.1:8000/docs

Health check:
http://127.0.0.1:8000/health

## Test request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/chart" \
  -H "Content-Type: application/json" \
  -d "{\"date\":\"2000-04-04\",\"time\":\"10:32\",\"place\":\"Mumbai, Maharashtra, India\"}"
```

PowerShell:

```powershell
$body = @{
  date = "2000-04-04"
  time = "10:32"
  place = "Mumbai, Maharashtra, India"
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/chart" `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

## Important production note

For a commercial application, do not rely on a public Nominatim endpoint for high-volume geocoding. Put a proper geocoding provider behind `app/services/geocoding.py` and cache place lookups.

Every hosted or modified deployment must preserve the AGPL notices and provide
a prominent link to its complete corresponding source code. A proprietary fork
requires separately obtaining all necessary commercial third-party licences.

## Web frontend

The React and TypeScript client lives in `web/`. It provides secure OIDC/PKCE
sign-in, saved birth profiles, persistent conversations, and the first chat
experience over the existing deterministic API. See
[`docs/frontend.md`](docs/frontend.md) for local and deployment configuration.
