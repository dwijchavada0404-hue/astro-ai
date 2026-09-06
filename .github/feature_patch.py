from pathlib import Path


app_path = Path("web/src/App.tsx")
text = app_path.read_text(encoding="utf-8")

old_storage = (
    "Application data is hosted on Railway in the EU region. Authentication is provided by Auth0 in the EU region. "
    "These providers process information on AstroAI’s behalf under their respective security and privacy terms. "
    "Internet access may involve processing across countries."
)
new_storage = (
    "Application data is hosted on Railway. Authentication is provided by Auth0. "
    "These providers process information on AstroAI’s behalf under their respective security and privacy terms. "
    "Internet access and service delivery may involve processing across countries."
)

if old_storage not in text:
    raise SystemExit("Expected privacy hosting disclosure was not found; refusing an unsafe broad replacement.")
if "Last updated 30 August 2026" not in text:
    raise SystemExit("Expected legal notice date was not found.")

text = text.replace(old_storage, new_storage, 1)
text = text.replace("Last updated 30 August 2026", "Last updated 6 September 2026", 1)
app_path.write_text(text, encoding="utf-8")
