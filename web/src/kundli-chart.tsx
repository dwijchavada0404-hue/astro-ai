type PlanetPlacement = { house?: number; retrograde?: boolean };
type HousePlacement = { sign?: string; lord?: string };

export type KundliHouse = {
  number: number;
  sign: string;
  lord: string;
  planets: Array<{ name: string; retrograde: boolean }>;
};

export function kundliHouses(houses?: Record<string, HousePlacement>, planets?: Record<string, PlanetPlacement>): KundliHouse[] {
  const byHouse = new Map<number, Array<{ name: string; retrograde: boolean }>>();
  Object.entries(planets || {}).forEach(([name, planet]) => {
    if (typeof planet.house !== "number" || planet.house < 1 || planet.house > 12) return;
    const current = byHouse.get(planet.house) || [];
    current.push({ name, retrograde: Boolean(planet.retrograde) });
    byHouse.set(planet.house, current);
  });
  return Array.from({ length: 12 }, (_, index) => {
    const number = index + 1;
    const house = houses?.[String(number)] || {};
    return { number, sign: house.sign || "—", lord: house.lord || "—", planets: byHouse.get(number) || [] };
  });
}

const POSITIONS: Record<number, { x: number; y: number }> = {
  1:{x:50,y:18},2:{x:25,y:9},3:{x:9,y:25},4:{x:18,y:50},5:{x:9,y:75},6:{x:25,y:91},
  7:{x:50,y:82},8:{x:75,y:91},9:{x:91,y:75},10:{x:82,y:50},11:{x:91,y:25},12:{x:75,y:9},
};

export function NorthIndianKundli({ houses, planets }: { houses?: Record<string, HousePlacement>; planets?: Record<string, PlanetPlacement> }) {
  const rows = kundliHouses(houses, planets);
  return <div className="kundli-shell">
    <svg className="kundli-svg" viewBox="0 0 100 100" role="img" aria-labelledby="kundli-title kundli-desc">
      <title id="kundli-title">North Indian style birth chart</title>
      <desc id="kundli-desc">Twelve houses showing engine-calculated signs and planetary placements.</desc>
      <rect x="1" y="1" width="98" height="98" rx="2" className="kundli-line" />
      <path d="M1 1L99 99M99 1L1 99M1 50L50 1L99 50L50 99Z" className="kundli-line" />
      {rows.map((house) => {
        const pos = POSITIONS[house.number];
        const planetText = house.planets.map((planet) => `${planet.name}${planet.retrograde ? " ℞" : ""}`).join(" · ");
        return <g key={house.number} transform={`translate(${pos.x} ${pos.y})`}>
          <text className="kundli-house-number" textAnchor="middle" y="-3">{house.number}</text>
          <text className="kundli-sign" textAnchor="middle" y="2">{house.sign}</text>
          {planetText && <text className="kundli-planets" textAnchor="middle" y="7">{planetText}</text>}
        </g>;
      })}
    </svg>
    <p className="kundli-legend">House numbers, signs and planets come directly from the calculated chart. ℞ marks retrograde motion.</p>
  </div>;
}
