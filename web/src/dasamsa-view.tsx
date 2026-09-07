import { KundliChart } from "./kundli-chart";
import "./dasamsa-view.css";

type D10Planet = {
  sign?: string;
  d1_sign?: string;
  degree_dms?: string;
  house?: number;
  retrograde?: boolean;
  same_sign_as_d1?: boolean;
};

type D10Chart = {
  name?: string;
  ascendant?: { sign?: string; d1_sign?: string; degree_dms?: string; same_sign_as_d1?: boolean };
  planets?: Record<string, D10Planet>;
  houses?: Record<string, { sign?: string; lord?: string }>;
};

export function dasamsaPlanetRows(planets?: Record<string, D10Planet>) {
  return Object.entries(planets || {}).map(([name, planet]) => ({ name, ...planet }));
}

export function DasamsaView({ chart }: { chart?: D10Chart }) {
  if (!chart) return null;
  const planets = dasamsaPlanetRows(chart.planets);

  return <section className="dasamsa-section" aria-label="Dashamsha D10 career chart">
    <div className="dasamsa-heading">
      <div><span>Divisional chart · D10</span><h4>Dashamsha</h4><p>Career and public-role divisional chart derived by the backend from the Lahiri sidereal birth chart.</p></div>
      <div className="dasamsa-lagna"><span>D10 Lagna</span><strong>{chart.ascendant?.sign || "—"}</strong><small>{chart.ascendant?.degree_dms || "—"}</small></div>
    </div>
    <KundliChart houses={chart.houses} planets={chart.planets} />
    <div className="dasamsa-table-wrap"><table><thead><tr><th>Planet</th><th>D1 sign</th><th>D10 sign</th><th>D10 degree</th><th>D10 house</th><th>Motion</th></tr></thead><tbody>{planets.map((planet) => <tr key={planet.name}><td><strong>{planet.name}</strong></td><td>{planet.d1_sign || "—"}</td><td>{planet.sign || "—"}</td><td>{planet.degree_dms || "—"}</td><td>{planet.house || "—"}</td><td>{planet.retrograde ? "Retrograde" : "Direct"}</td></tr>)}</tbody></table></div>
    <p className="dasamsa-note">D10 uses the classical odd/even sign mapping in 3° segments. It refines career and public-role symbolism but does not override the natal chart or real-world facts.</p>
  </section>;
}
