from pathlib import Path

path = Path("web/src/App.test.tsx")
text = path.read_text(encoding="utf-8")
old = 'expect(screen.getByText(/Railway in the EU region/)).toBeInTheDocument();'
new = 'expect(screen.getByText(/Application data is hosted on Railway\\. Authentication is provided by Auth0\\./)).toBeInTheDocument();'
if old not in text:
    raise SystemExit("Expected old privacy assertion was not found.")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
