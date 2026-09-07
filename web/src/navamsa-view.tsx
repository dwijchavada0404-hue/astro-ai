import { KundliChart } from "./kundli-chart";
import "./navamsa-view.css";

type D9Planet = {
  sign?: string;
  d1_sign?: string;
  degree_dms?: string;
  house?: number;
  retrograde?: boolean;
  vargottama?: boolean;
};

type D9Chart = {
  name?: string;
  ascendant?: { sign?: string; d1_sign?: string; degree_dms?: string; vargottama?: boolean };
  planets?: Record<string, D9Planet>;
  houses?: Record<string, { sign?: string; lord?: string }>;
};

export function navamsaPlanetRows(planets?: Record<string, D9Planet>) {
  return Object.entries(planets || {}).map(([name, planet]) => ({ name, ...planet }));
}

export function NavamsaView({ chart }: { chart?: D9Chart }) {
  if (!chart) return null;
  const planets = navamsaPlanetRows(chart.planets);
  const vargottama = planets.filter((planet) => planet.vargottama);

  return <section className="navamsa-section" aria-label="Navamsa D9 chart">
    <div className="navamsa-heading">
      <div><span>Divisional chart · D9</span><h4>Navamsa</h4><p>Derived deterministically from the same Lahiri sidereal birth chart.</p></div>
      <div className="navamsa-lagna"><span>D9 Lagna</span><strong>{chart.ascendant?.sign || "—"}</strong><small>{chart.ascendant?.degree_dms || "—"}</small></div>
    </div>
    <KundliChart houses={chart.houses} planets={chart.planets} />
    <div className="navamsa-table-wrap"><table><thead><tr><th>Planet</th><th>D1 sign</th><th>D9 sign</th><th>D9 degree</th><th>D9 house</th><th>Status</th></tr></thead><tbody>{planets.map((planet) => <tr key={planet.name}><td><strong>{planet.name}{planet.retrograde ? " ℞" : ""}</strong></td><td>{planet.d1_sign || "—"}</td><td>{planet.sign || "—"}</td><td>{planet.degree_dms || "—"}</td><td>{planet.house || "—"}</td><td>{planet.vargottama ? <span className="vargottama-badge">Vargottama</span> : "—"}</td></tr>)}</tbody></table></div>
    <p className="navamsa-note">{vargottama.length > 0 ? `${vargottama.length} Vargottama placement${vargottama.length === 1 ? "" : "s"} shown where D1 and D9 signs match.` : "No planetary Vargottama placements in this calculated D9."} D9 is displayed as a traditional divisional chart for reflection and entertainment.</p>
  </section>;
}
