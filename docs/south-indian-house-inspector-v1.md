# South Indian House Inspector V1

The South Indian Kundli now has the same house-detail inspection experience as the North Indian layout.

## Behaviour

- The Lagna / House 1 sign is selected by default when available.
- Every fixed South Indian sign cell is a keyboard-accessible button.
- Selecting a sign shows its backend-derived house number, house lord, planets, retrograde status, degree and nakshatra.
- Empty houses are explicitly identified.
- If a partial chart response lacks a house mapping, the cell remains safely inspectable without inventing a house number or lord.
- North Indian inspection behaviour is preserved.

The frontend does not calculate signs, houses, lords, planetary degrees, nakshatras or retrograde motion. It only presents deterministic saved-profile chart data returned by the AstroAI engine.
