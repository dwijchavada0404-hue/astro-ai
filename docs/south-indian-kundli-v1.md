# South Indian Kundli V1

The saved Birth Chart Viewer supports both North Indian and South Indian visual layouts for the same deterministic chart.

## Behaviour

- North Indian remains the default and keeps the interactive house inspector introduced in Kundli House Inspector V1.
- Users can switch between North Indian and South Indian layouts without refetching or recalculating the chart.
- South Indian layout keeps zodiac signs fixed in the traditional 4×4 perimeter: Pisces, Aries, Taurus and Gemini across the top, continuing clockwise through Cancer, Leo, Virgo, Libra, Scorpio, Sagittarius, Capricorn and Aquarius.
- House numbers come from the backend `houses` mapping. The sign assigned to House 1 is marked as Lagna.
- Planet placements come from the backend planet `sign` field, with the backend house sign used only as a display fallback if a planet sign is absent.
- Retrograde markers reuse the backend `retrograde` boolean.

No astrological positions are computed in the frontend; the UI only reformats deterministic engine output.
