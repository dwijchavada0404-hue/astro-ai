# Vimshottari Mahadasha Timeline V1

The saved Birth Chart Viewer exposes the Mahadasha sequence already returned by AstroAI's deterministic chart engine.

## Behaviour

- The frontend does not calculate or reinterpret dasha dates.
- Mahadashas are rendered in the order returned by `chart.dashas.mahadashas`.
- The active Mahadasha is highlighted by matching `chart.dashas.current_period.mahadasha`.
- Period dates use the existing timezone-safe date formatter so ISO offsets do not shift the displayed calendar day.
- The timeline is responsive and collapses to a single column on small screens.

The timeline complements the current Mahadasha/Antardasha panel and is for reflection and entertainment, consistent with the rest of AstroAI.
