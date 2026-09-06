import { useEffect, useState } from "react";
import { apiRequest, type BirthProfile } from "./api";

type Planet = {
  sign?: string;
  degree_in_sign?: number;
  degree_dms?: string;
  house?: number;
  nakshatra?: string;
  retrograde?: boolean;
};

type House = { sign?: string; lord?: string };

type Antardasha = { planet?: string; start?: string; end?: string; duration_years?: number };
type Mahadasha = { planet?: string; start?: string; end?: string; duration_years?: number; antardashas?: Antardasha[] };

type CurrentPeriod = {
  mahadasha?: string;
  mahadasha_start?: string;
  mahadasha_end?: string;
  antardasha?: string;
  antardasha_start?: string;
  antardasha_end?: string;
};

type Dashas = {
  system?: string;
  moon_nakshatra?: string;
  first_mahadasha_lord?: string;
  current_period?: CurrentPeriod | null;
  mahadashas?: Mahadasha[];
};

type Chart = {
  methodology?: Record<string, unknown>;
  birth?: Record<string, unknown>;
  ascendant?: { sign?: string; degree_in_sign?: number; degree_dms?: string };
  planets?: Record<string, Planet>;
  houses?: Record<string, House>;
  dashas?: Dashas;
};

type ChartResponse = {
  birth_profile: { profile_id: string; label: string; is_default: boolean };
  birth_source: "saved_profile";
  chart: Chart;
};

export function formatDegree(value?: number, dms?: string): string {
  if (dms) return dms;
  return typeof value === "number" ? `${value.toFixed(2)}°` : "—";
}

export function planetRows(planets?: Record<string, Planet>) {
  return Object.entries(planets || {}).map(([name, planet]) => ({ name, ...planet }));
}

export function formatPeriodDate(value?: string): string {
  if (!value) return "—";
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})/);
  return match ? `${match[3]} ${["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][Number(match[2]) - 1]} ${match[1]}` : "—";
}

export function currentDashaLabel(period?: CurrentPeriod | null): string {
  if (!period?.mahadasha || !period?.antardasha) return "Current period unavailable";
  return `${period.mahadasha} Mahadasha · ${period.antardasha} Antardasha`;
}

export function mahadashaRows(dashas?: Dashas): Array<Mahadasha & { isCurrent: boolean }> {
  const currentLord = dashas?.current_period?.mahadasha;
  return (dashas?.mahadashas || []).map((period) => ({ ...period, isCurrent: Boolean(currentLord && period.planet === currentLord) }));
}

export function BirthChartViewer({ token, profile, onClose }: { token: string; profile: BirthProfile; onClose: () => void }) {
  const [data, setData] = useState<ChartResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    apiRequest<ChartResponse>(`/api/v1/birth-profiles/${profile.profile_id}/chart`, token)
      .then((response) => { if (active) setData(response); })
      .catch((reason) => { if (active) setError(reason instanceof Error ? reason.message : "The birth chart could not be calculated."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [profile.profile_id, token]);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  const chart = data?.chart;
  const rows = planetRows(chart?.planets);
  const houses = Object.entries(chart?.houses || {});
  const methodology = chart?.methodology || {};
  const currentPeriod = chart?.dashas?.current_period;
  const timeline = mahadashaRows(chart?.dashas);

  return <div className="chart-scrim" role="presentation">
    <section className="chart-dialog" role="dialog" aria-modal="true" aria-labelledby="birth-chart-title">
      <div className="chart-heading">
        <div><span>Deterministic Vedic chart</span><h3 id="birth-chart-title">{profile.label}</h3><p>{profile.birth_date} · {profile.birth_time.slice(0, 5)} · {profile.place}</p></div>
        <button type="button" aria-label="Close birth chart" onClick={onClose}>×</button>
      </div>
      {loading && <div className="chart-loading" role="status">Calculating your sidereal chart…</div>}
      {error && <div className="error-banner">{error}</div>}
      {chart && <div className="chart-content">
        <section className="chart-summary">
          <article><span>Ascendant</span><strong>{chart.ascendant?.sign || "—"}</strong><small>{formatDegree(chart.ascendant?.degree_in_sign, chart.ascendant?.degree_dms)}</small></article>
          <article><span>Zodiac</span><strong>{String(methodology.zodiac || "sidereal")}</strong><small>{String(methodology.ayanamsa || "Lahiri")} ayanamsa</small></article>
          <article><span>Houses</span><strong>{String(methodology.house_system || "Whole Sign")}</strong><small>{String(methodology.ephemeris || "Swiss Ephemeris")}</small></article>
        </section>
        <section className="current-dasha" aria-label="Current Vimshottari timing">
          <div><span>Current Vimshottari timing</span><h4>{currentDashaLabel(currentPeriod)}</h4><p>Moon nakshatra: <strong>{chart.dashas?.moon_nakshatra || "—"}</strong></p></div>
          {currentPeriod && <div className="dasha-periods"><article><span>Mahadasha</span><strong>{currentPeriod.mahadasha || "—"}</strong><small>{formatPeriodDate(currentPeriod.mahadasha_start)} → {formatPeriodDate(currentPeriod.mahadasha_end)}</small></article><article><span>Antardasha</span><strong>{currentPeriod.antardasha || "—"}</strong><small>{formatPeriodDate(currentPeriod.antardasha_start)} → {formatPeriodDate(currentPeriod.antardasha_end)}</small></article></div>}
        </section>
        {timeline.length > 0 && <section className="chart-section"><div className="chart-section-title"><h4>Vimshottari Mahadasha timeline</h4><span>120-year deterministic sequence</span></div><div className="dasha-timeline">{timeline.map((period, index) => <article key={`${period.planet || "period"}-${period.start || index}`} className={period.isCurrent ? "is-current" : ""} aria-current={period.isCurrent ? "true" : undefined}><span>{period.isCurrent ? "Current Mahadasha" : `Period ${index + 1}`}</span><strong>{period.planet || "—"}</strong><small>{formatPeriodDate(period.start)} → {formatPeriodDate(period.end)}</small></article>)}</div></section>}
        <section className="chart-section"><div className="chart-section-title"><h4>Planetary positions</h4><span>Calculated at birth</span></div><div className="chart-table-wrap"><table><thead><tr><th>Planet</th><th>Sign</th><th>Degree</th><th>House</th><th>Nakshatra</th><th>Motion</th></tr></thead><tbody>{rows.map((planet) => <tr key={planet.name}><td><strong>{planet.name}</strong></td><td>{planet.sign || "—"}</td><td>{formatDegree(planet.degree_in_sign, planet.degree_dms)}</td><td>{planet.house || "—"}</td><td>{planet.nakshatra || "—"}</td><td>{planet.retrograde ? "Retrograde" : "Direct"}</td></tr>)}</tbody></table></div></section>
        <section className="chart-section"><div className="chart-section-title"><h4>Whole Sign houses</h4><span>Sign and house lord</span></div><div className="house-grid">{houses.map(([number, house]) => <article key={number}><span>House {number}</span><strong>{house.sign || "—"}</strong><small>Lord: {house.lord || "—"}</small></article>)}</div></section>
        <p className="chart-footnote">Calculated from your saved birth details using the deterministic AstroAI engine. Current timing is evaluated when the chart is opened. Astrology is for reflection and entertainment.</p>
      </div>}
    </section>
  </div>;
}
