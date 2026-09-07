# Navamsa (D9) V1

AstroAI now calculates and displays a deterministic Navamsa (D9) divisional chart from the same Lahiri sidereal D1 positions used by the natal chart.

## Calculation

- The zodiac is divided into 108 Navamsa segments of 3°20′ each.
- D9 longitude is derived as `9 × sidereal longitude mod 360`, which is equivalent to the classical rule: movable signs start from themselves, fixed signs from the ninth sign, and dual signs from the fifth sign.
- The D9 Ascendant is calculated from the D1 sidereal Ascendant longitude using the same mapping.
- D9 Whole Sign houses are counted from the D9 Ascendant sign.
- Vargottama is flagged when a planet or Ascendant occupies the same sign in D1 and D9.
- Retrograde status is carried from the natal planetary calculation; it is not recalculated from D9 longitude.

## Product behaviour

The saved Birth Chart Viewer shows:

- D9 Lagna and degree
- North/South Indian D9 Kundli using the shared chart renderer
- D1 sign vs D9 sign for each planet
- D9 house and degree
- Vargottama markers

The frontend does not perform Navamsa arithmetic. It only renders `chart.divisional_charts.D9` returned by the backend.
