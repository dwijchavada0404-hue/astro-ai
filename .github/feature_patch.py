from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "web" / "src" / "App.tsx"
STYLES = ROOT / "web" / "src" / "styles.css"
TEST = ROOT / "web" / "src" / "profile-correction.test.tsx"

app = APP.read_text(encoding="utf-8")

state_old = '  const [restoreNotice, setRestoreNotice] = useState("");\n'
state_new = '''  const [restoreNotice, setRestoreNotice] = useState("");
  const [correctionProfile, setCorrectionProfile] = useState<BirthProfile | null>(null);
  const [correctionForm, setCorrectionForm] = useState({ label: "", date: "", time: "", place: "" });
'''
assert state_old in app
app = app.replace(state_old, state_new, 1)

old_handler = '''  const duplicateAndCorrectProfile = async (profile: BirthProfile) => {
    const requestedLabel = window.prompt("Name the corrected birth profile", `${profile.label} (corrected)`);
    if (requestedLabel === null) return;
    const label = requestedLabel.trim().replace(/\\s+/g, " ");
    if (!label) { setError("Profile name cannot be empty."); return; }
    if (label.length > 80) { setError("Profile name must be 80 characters or fewer."); return; }
    const date = window.prompt("Correct birth date (YYYY-MM-DD)", profile.birth_date);
    if (date === null) return;
    const time = window.prompt("Correct exact birth time (HH:MM)", profile.birth_time.slice(0, 5));
    if (time === null) return;
    const place = window.prompt("Correct birth place", profile.place);
    if (place === null) return;
    if (!date.trim() || !time.trim() || !place.trim()) { setError("Birth date, exact time and place are required."); return; }

    setBusy(true);
    setError("");
    try {
      const duplicated = await apiRequest<{ birth_profile: BirthProfile }>(`/api/v1/birth-profiles/${profile.profile_id}/duplicate`, token, {
        method: "POST",
        body: JSON.stringify({ label }),
      });
      await apiRequest(`/api/v1/birth-profiles/${duplicated.birth_profile.profile_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ date: date.trim(), time: time.trim(), place: place.trim() }),
      });
      await onCreated();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };
'''
new_handler = '''  const openProfileCorrection = (profile: BirthProfile) => {
    setError("");
    setRestoreNotice("");
    setCorrectionProfile(profile);
    setCorrectionForm({
      label: `${profile.label} (corrected)`,
      date: profile.birth_date,
      time: profile.birth_time.slice(0, 5),
      place: profile.place,
    });
  };

  const submitProfileCorrection = async (event: FormEvent) => {
    event.preventDefault();
    if (!correctionProfile) return;
    const label = correctionForm.label.trim().replace(/\\s+/g, " ");
    const date = correctionForm.date.trim();
    const time = correctionForm.time.trim();
    const place = correctionForm.place.trim();
    if (!label) { setError("Profile name cannot be empty."); return; }
    if (label.length > 80) { setError("Profile name must be 80 characters or fewer."); return; }
    if (!date || !time || !place) { setError("Birth date, exact time and place are required."); return; }

    setBusy(true);
    setError("");
    try {
      const duplicated = await apiRequest<{ birth_profile: BirthProfile }>(`/api/v1/birth-profiles/${correctionProfile.profile_id}/duplicate`, token, {
        method: "POST",
        body: JSON.stringify({ label }),
      });
      await apiRequest(`/api/v1/birth-profiles/${duplicated.birth_profile.profile_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ date, time, place }),
      });
      await onCreated();
      setCorrectionProfile(null);
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };
'''
assert old_handler in app
app = app.replace(old_handler, new_handler, 1)

button_old = '<button type="button" onClick={() => duplicateAndCorrectProfile(profile)} disabled={busy}>Duplicate &amp; correct</button>'
button_new = '<button type="button" onClick={() => openProfileCorrection(profile)} disabled={busy}>Duplicate &amp; correct</button>'
assert button_old in app
app = app.replace(button_old, button_new, 1)

panel_marker = '    </article>)}</div>\n    <form className="profile-form"'
panel = '''    </article>)}</div>
    {correctionProfile && <div className="correction-scrim" role="presentation">
      <section className="correction-dialog" role="dialog" aria-modal="true" aria-labelledby="profile-correction-title">
        <form onSubmit={submitProfileCorrection}>
          <div className="correction-heading"><div><span>Safe profile correction</span><h3 id="profile-correction-title">Duplicate &amp; correct {correctionProfile.label}</h3></div><button type="button" aria-label="Close correction form" onClick={() => setCorrectionProfile(null)} disabled={busy}>×</button></div>
          <p className="correction-note">A new birth profile will be created first. Your original profile and every conversation already linked to it stay unchanged.</p>
          <label>Corrected profile name<input aria-label="Corrected profile name" value={correctionForm.label} onChange={(event) => setCorrectionForm({ ...correctionForm, label: event.target.value })} maxLength={80} required autoFocus /></label>
          <div className="correction-fields"><label>Birth date<input aria-label="Corrected birth date" type="date" value={correctionForm.date} onChange={(event) => setCorrectionForm({ ...correctionForm, date: event.target.value })} required /></label><label>Exact birth time<input aria-label="Corrected birth time" type="time" value={correctionForm.time} onChange={(event) => setCorrectionForm({ ...correctionForm, time: event.target.value })} required /></label></div>
          <label>Birth place<input aria-label="Corrected birth place" value={correctionForm.place} onChange={(event) => setCorrectionForm({ ...correctionForm, place: event.target.value })} maxLength={200} required /></label>
          <div className="correction-actions"><button type="button" onClick={() => setCorrectionProfile(null)} disabled={busy}>Cancel</button><button className="primary" disabled={busy}>{busy ? "Saving corrected copy…" : "Save corrected copy"}</button></div>
        </form>
      </section>
    </div>}
    <form className="profile-form"'''
assert panel_marker in app
app = app.replace(panel_marker, panel, 1)
APP.write_text(app, encoding="utf-8")

styles = STYLES.read_text(encoding="utf-8")
style_block = '''
.correction-scrim{position:fixed;inset:0;z-index:40;background:rgba(2,4,12,.76);display:grid;place-items:center;padding:1.25rem;backdrop-filter:blur(6px)}.correction-dialog{width:min(620px,100%);max-height:calc(100vh - 2.5rem);overflow:auto;background:#111528;border:1px solid rgba(155,135,245,.28);border-radius:16px;box-shadow:0 28px 80px rgba(0,0,0,.48)}.correction-dialog form{padding:1.5rem}.correction-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:1rem}.correction-heading span{color:var(--gold);font-size:.68rem;letter-spacing:.12em;text-transform:uppercase}.correction-heading h3{font-family:Manrope;font-weight:500;margin:.35rem 0 0}.correction-heading button{width:34px;height:34px;border:1px solid var(--line);border-radius:8px;background:#191e33;color:#dcd8ed;font-size:1.15rem}.correction-note{color:#9ba2b7;line-height:1.55;font-size:.84rem;margin:1rem 0 1.3rem}.correction-dialog label{display:flex;flex-direction:column;gap:.42rem;color:#a7adbf;font-size:.78rem;margin-bottom:1rem}.correction-dialog input{background:#0c0f1c;border:1px solid var(--line);color:#fff;border-radius:8px;padding:.75rem;outline:none}.correction-dialog input:focus{border-color:var(--violet)}.correction-fields{display:grid;grid-template-columns:1fr 1fr;gap:1rem}.correction-actions{display:flex;justify-content:flex-end;gap:.7rem;margin-top:.35rem}.correction-actions button{border:1px solid var(--line);background:#191e33;color:#dcd8ed;border-radius:8px;padding:.7rem .9rem}.correction-actions .primary{border:0;color:#090b16;background:linear-gradient(135deg,#bcaafc,#8e78eb)}.correction-actions button:disabled,.correction-heading button:disabled{opacity:.5;cursor:not-allowed}@media(max-width:600px){.correction-fields{grid-template-columns:1fr}.correction-dialog form{padding:1.15rem}.correction-actions{flex-direction:column-reverse}.correction-actions button{width:100%}}
'''
if '.correction-scrim{' not in styles:
    STYLES.write_text(styles.rstrip() + "\n" + style_block, encoding="utf-8")

TEST.write_text('''import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Profiles } from "./App";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const source = {
  profile_id: "source-profile",
  label: "My chart",
  birth_date: "2000-04-04",
  birth_time: "14:04:00",
  place: "Borivali, Mumbai",
  is_default: true,
};

describe("birth profile correction workflow", () => {
  it("opens a prefilled in-app correction form", () => {
    render(<Profiles token="token" profiles={[source]} onCreated={vi.fn().mockResolvedValue(undefined)} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));

    expect(screen.getByRole("dialog", { name: /Duplicate & correct My chart/ })).toBeInTheDocument();
    expect(screen.getByLabelText("Corrected profile name")).toHaveValue("My chart (corrected)");
    expect(screen.getByLabelText("Corrected birth date")).toHaveValue("2000-04-04");
    expect(screen.getByLabelText("Corrected birth time")).toHaveValue("14:04");
    expect(screen.getByLabelText("Corrected birth place")).toHaveValue("Borivali, Mumbai");
    expect(screen.getByText(/original profile and every conversation already linked to it stay unchanged/i)).toBeInTheDocument();
  });

  it("duplicates a profile before applying corrected birth details", async () => {
    const duplicate = {
      ...source,
      profile_id: "corrected-profile",
      label: "My chart corrected",
      is_default: false,
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 201, json: async () => ({ birth_profile: duplicate }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profile: { ...duplicate, birth_time: "14:06:00" } }) });
    vi.stubGlobal("fetch", fetchMock);
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" profiles={[source]} onCreated={onCreated} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));
    fireEvent.change(screen.getByLabelText("Corrected profile name"), { target: { value: "My chart corrected" } });
    fireEvent.change(screen.getByLabelText("Corrected birth time"), { target: { value: "14:06" } });
    fireEvent.click(screen.getByRole("button", { name: "Save corrected copy" }));

    await waitFor(() => expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining("/api/v1/birth-profiles/source-profile/duplicate"),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ label: "My chart corrected" }) }),
    ));
    await waitFor(() => expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining("/api/v1/birth-profiles/corrected-profile"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ date: "2000-04-04", time: "14:06", place: "Borivali, Mumbai" }) }),
    ));
    expect(onCreated).toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("does not create a duplicate when correction is cancelled", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    render(<Profiles token="token" profiles={[source]} onCreated={vi.fn().mockResolvedValue(undefined)} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});
''', encoding="utf-8")
