# Dashamsha (D10) V1

AstroAI calculates and displays a deterministic Dashamsha (D10) divisional chart from the same Lahiri sidereal D1 positions used by the natal chart.

## Calculation

- Each 30° sign is divided into ten 3° Dashamsha parts.
- For odd zodiac signs, the first part begins from the natal sign and subsequent parts advance sign by sign.
- For even zodiac signs, the first part begins from the ninth sign counted from the natal sign and subsequent parts advance sign by sign.
- D10 Ascendant uses the same rule applied to the sidereal D1 Ascendant longitude.
- D10 Whole Sign houses are counted from the D10 Ascendant sign.
- Retrograde status is carried from the natal planetary calculation; it is not recalculated from D10 longitude.

This intentionally does **not** use a simple harmonic `10 × longitude` shortcut because the classical odd/even Dashamsha mapping is asymmetric.

## Product behaviour

The saved Birth Chart Viewer shows:

- D10 Lagna and degree
- North/South Indian D10 Kundli using the shared deterministic chart renderer
- D1 sign vs D10 sign for each planet
- D10 house and degree
- retrograde status

D10 provides career/public-role symbolism and does not override the natal chart or known real-world facts. The frontend performs no Dashamsha arithmetic; it only renders `chart.divisional_charts.D10` returned by the backend.
