from pathlib import Path

app_path = Path("web/src/App.tsx")
app = app_path.read_text(encoding="utf-8")

old_import = 'import { parseAstroAiBackup } from "./backup";\n'
new_import = old_import + 'import { BirthChartViewer } from "./chart-viewer";\n'
if 'from "./chart-viewer"' not in app:
    if old_import not in app:
        raise SystemExit("App import anchor not found")
    app = app.replace(old_import, new_import, 1)

old_state = '  const [correctionProfile, setCorrectionProfile] = useState<BirthProfile | null>(null);\n  const [correctionForm, setCorrectionForm] = useState({ label: "", date: "", time: "", place: "" });'
new_state = '  const [correctionProfile, setCorrectionProfile] = useState<BirthProfile | null>(null);\n  const [chartProfile, setChartProfile] = useState<BirthProfile | null>(null);\n  const [correctionForm, setCorrectionForm] = useState({ label: "", date: "", time: "", place: "" });'
if 'const [chartProfile, setChartProfile]' not in app:
    if old_state not in app:
        raise SystemExit("Profiles state anchor not found")
    app = app.replace(old_state, new_state, 1)

old_actions = '        {!profile.is_default && <button type="button" onClick={() => setDefault(profile)} disabled={busy}>Make default</button>}\n        <button type="button" onClick={() => renameProfile(profile)} disabled={busy}>Rename</button>'
new_actions = '        <button type="button" className="view-chart" onClick={() => { setError(""); setChartProfile(profile); }} disabled={busy}>View chart</button>\n        {!profile.is_default && <button type="button" onClick={() => setDefault(profile)} disabled={busy}>Make default</button>}\n        <button type="button" onClick={() => renameProfile(profile)} disabled={busy}>Rename</button>'
if 'className="view-chart"' not in app:
    if old_actions not in app:
        raise SystemExit("Profile action anchor not found")
    app = app.replace(old_actions, new_actions, 1)

old_dialog = '    {correctionProfile && <div className="correction-scrim" role="presentation">'
new_dialog = '    {chartProfile && <BirthChartViewer token={token} profile={chartProfile} onClose={() => setChartProfile(null)} />}\n    {correctionProfile && <div className="correction-scrim" role="presentation">'
if 'chartProfile && <BirthChartViewer' not in app:
    if old_dialog not in app:
        raise SystemExit("Correction dialog anchor not found")
    app = app.replace(old_dialog, new_dialog, 1)

app_path.write_text(app, encoding="utf-8")

main_path = Path("web/src/main.tsx")
main = main_path.read_text(encoding="utf-8")
css_import = 'import "./chart-viewer.css";\n'
if css_import not in main:
    anchor = 'import "./backup.css";\n'
    if anchor not in main:
        raise SystemExit("main CSS anchor not found")
    main = main.replace(anchor, anchor + css_import, 1)
main_path.write_text(main, encoding="utf-8")
