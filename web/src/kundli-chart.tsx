import { useState } from "react";

type PlanetPlacement = { house?: number; retrograde?: boolean; sign?: string; degree_dms?: string; nakshatra?: string };
type HousePlacement = { sign?: string; lord?: string };
type KundliPlanet = { name: string; retrograde: boolean; degree?: string; nakshatra?: string };

export type KundliHouse = {
  number: number;
  sign: string;
  lord: string;
  planets: KundliPlanet[];
};

export type SouthIndianCell = {
  sign: string;
  houseNumber?: number;
  lord: string;
  planets: KundliPlanet[];
};

function enginePlanet(name: string, planet: PlanetPlacement): KundliPlanet {
  return { name, retrograde: Boolean(planet.retrograde), degree: planet.degree_dms, nakshatra: planet.nakshatra };
}

export function kundliHouses(houses?: Record<string, HousePlacement>, planets?: Record<string, PlanetPlacement>): KundliHouse[] {
  const byHouse = new Map<number, KundliPlanet[]>();
  Object.entries(planets || {}).forEach(([name, planet]) => {
    if (typeof planet.house !== "number" || planet.house < 1 || planet.house > 12) return;
    const current = byHouse.get(planet.house) || [];
    current.push(enginePlanet(name, planet));
    byHouse.set(planet.house, current);
  });
  return Array.from({ length: 12 }, (_, index) => {
    const number = index + 1;
    const house = houses?.[String(number)] || {};
    return { number, sign: house.sign || "—", lord: house.lord || "—", planets: byHouse.get(number) || [] };
  });
}

export const SOUTH_INDIAN_SIGNS = [
  "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo",
  "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
] as const;

export function southIndianCells(houses?: Record<string, HousePlacement>, planets?: Record<string, PlanetPlacement>): SouthIndianCell[] {
  const houseBySign = new Map<string, { number: number; lord: string }>();
  Object.entries(houses || {}).forEach(([number, house]) => {
    const parsed = Number(number);
    if (house.sign && Number.isInteger(parsed) && parsed >= 1 && parsed <= 12) {
      houseBySign.set(house.sign, { number: parsed, lord: house.lord || "—" });
    }
  });

  const planetsBySign = new Map<string, KundliPlanet[]>();
  Object.entries(planets || {}).forEach(([name, planet]) => {
    const fallbackSign = typeof planet.house === "number" ? houses?.[String(planet.house)]?.sign : undefined;
    const sign = planet.sign || fallbackSign;
    if (!sign || !SOUTH_INDIAN_SIGNS.includes(sign as (typeof SOUTH_INDIAN_SIGNS)[number])) return;
    const current = planetsBySign.get(sign) || [];
    current.push(enginePlanet(name, planet));
    planetsBySign.set(sign, current);
  });

  return SOUTH_INDIAN_SIGNS.map((sign) => {
    const house = houseBySign.get(sign);
    return { sign, houseNumber: house?.number, lord: house?.lord || "—", planets: planetsBySign.get(sign) || [] };
  });
}

const POSITIONS: Record<number, { x: number; y: number }> = {
  1:{x:50,y:18},2:{x:25,y:9},3:{x:9,y:25},4:{x:18,y:50},5:{x:9,y:75},6:{x:25,y:91},
  7:{x:50,y:82},8:{x:75,y:91},9:{x:91,y:75},10:{x:82,y:50},11:{x:91,y:25},12:{x:75,y:9},
};

const SOUTH_GRID_AREAS: Record<string, string> = {
  Pisces:"1 / 1", Aries:"1 / 2", Taurus:"1 / 3", Gemini:"1 / 4",
  Aquarius:"2 / 1", Cancer:"2 / 4", Capricorn:"3 / 1", Leo:"3 / 4",
  Sagittarius:"4 / 1", Scorpio:"4 / 2", Libra:"4 / 3", Virgo:"4 / 4",
};

function HouseInspector({ houseNumber, sign, lord, planets }: { houseNumber?: number; sign: string; lord: string; planets: KundliPlanet[] }) {
  return <section className="kundli-inspector" aria-live="polite" aria-label={houseNumber ? `House ${houseNumber} details` : `${sign} sign details`}>
    <div className="kundli-inspector-heading"><div><span>Selected house</span><h5>{houseNumber ? `House ${houseNumber} · ${sign}` : `${sign} · House unavailable`}</h5></div><small>Lord: <strong>{lord}</strong></small></div>
    {planets.length > 0 ? <div className="kundli-planet-grid">{planets.map((planet) => <article key={planet.name}><span>{planet.retrograde ? "Retrograde planet" : "Planet"}</span><strong>{planet.name}{planet.retrograde ? " ℞" : ""}</strong><small>{planet.degree || "Degree unavailable"}</small><small>{planet.nakshatra || "Nakshatra unavailable"}</small></article>)}</div> : <p className="kundli-empty">No planets are placed in this house in the calculated natal chart.</p>}
  </section>;
}

export function NorthIndianKundli({ houses, planets }: { houses?: Record<string, HousePlacement>; planets?: Record<string, PlanetPlacement> }) {
  const rows = kundliHouses(houses, planets);
  const [selectedHouseNumber, setSelectedHouseNumber] = useState(1);
  const selectedHouse = rows[selectedHouseNumber - 1];
  return <div className="kundli-shell">
    <svg className="kundli-svg" viewBox="0 0 100 100" role="img" aria-labelledby="north-kundli-title north-kundli-desc">
      <title id="north-kundli-title">North Indian style birth chart</title>
      <desc id="north-kundli-desc">Twelve houses showing engine-calculated signs and planetary placements. Select a house to inspect its details.</desc>
      <rect x="1" y="1" width="98" height="98" rx="2" className="kundli-line" />
      <path d="M1 1L99 99M99 1L1 99M1 50L50 1L99 50L50 99Z" className="kundli-line" />
      {rows.map((house) => {
        const pos = POSITIONS[house.number];
        const planetText = house.planets.map((planet) => `${planet.name}${planet.retrograde ? " ℞" : ""}`).join(" · ");
        const selected = house.number === selectedHouseNumber;
        return <g key={house.number} transform={`translate(${pos.x} ${pos.y})`} role="button" tabIndex={0} aria-label={`House ${house.number}, ${house.sign}, ${house.planets.length} planets`} aria-pressed={selected} className={`kundli-house ${selected ? "is-selected" : ""}`} onClick={() => setSelectedHouseNumber(house.number)} onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") { event.preventDefault(); setSelectedHouseNumber(house.number); } }}>
          <circle className="kundli-hit" r="8" />
          <text className="kundli-house-number" textAnchor="middle" y="-3">{house.number}</text>
          <text className="kundli-sign" textAnchor="middle" y="2">{house.sign}</text>
          {planetText && <text className="kundli-planets" textAnchor="middle" y="7">{planetText}</text>}
        </g>;
      })}
    </svg>
    <HouseInspector houseNumber={selectedHouse.number} sign={selectedHouse.sign} lord={selectedHouse.lord} planets={selectedHouse.planets} />
    <p className="kundli-legend">Select any house for details. House numbers, signs, lords and planets come directly from the calculated chart. ℞ marks retrograde motion.</p>
  </div>;
}

export function SouthIndianKundli({ houses, planets }: { houses?: Record<string, HousePlacement>; planets?: Record<string, PlanetPlacement> }) {
  const cells = southIndianCells(houses, planets);
  const lagnaCell = cells.find((cell) => cell.houseNumber === 1) || cells[0];
  const [selectedSign, setSelectedSign] = useState(lagnaCell.sign);
  const selectedCell = cells.find((cell) => cell.sign === selectedSign) || lagnaCell;
  return <div className="kundli-shell">
    <div className="south-kundli" role="group" aria-label="South Indian style birth chart with selectable fixed zodiac signs">
      {cells.map((cell) => {
        const selected = cell.sign === selectedCell.sign;
        return <button type="button" key={cell.sign} className={`south-kundli-cell ${cell.houseNumber === 1 ? "is-lagna" : ""} ${selected ? "is-selected" : ""}`.trim()} style={{ gridArea: SOUTH_GRID_AREAS[cell.sign] }} aria-label={`${cell.sign}, ${cell.houseNumber ? `House ${cell.houseNumber}` : "house unavailable"}, ${cell.planets.length} planets`} aria-pressed={selected} onClick={() => setSelectedSign(cell.sign)}>
          <span>{cell.houseNumber === 1 ? "Lagna · House 1" : cell.houseNumber ? `House ${cell.houseNumber}` : ""}</span>
          <strong>{cell.sign}</strong>
          {cell.planets.length > 0 && <small>{cell.planets.map((planet) => `${planet.name}${planet.retrograde ? " ℞" : ""}`).join(" · ")}</small>}
        </button>;
      })}
      <div className="south-kundli-center" aria-hidden="true"><strong>South Indian</strong><span>Fixed signs</span></div>
    </div>
    <HouseInspector houseNumber={selectedCell.houseNumber} sign={selectedCell.sign} lord={selectedCell.lord} planets={selectedCell.planets} />
    <p className="kundli-legend">Select any sign cell for house details. South Indian signs stay fixed while houses rotate from the Lagna; all house, lord and planet details come directly from the calculated chart.</p>
  </div>;
}

export function KundliChart({ houses, planets }: { houses?: Record<string, HousePlacement>; planets?: Record<string, PlanetPlacement> }) {
  const [style, setStyle] = useState<"north" | "south">("north");
  return <div className="kundli-viewer">
    <div className="kundli-style-switcher" role="group" aria-label="Kundli chart style">
      <button type="button" className={style === "north" ? "is-active" : ""} aria-pressed={style === "north"} onClick={() => setStyle("north")}>North Indian</button>
      <button type="button" className={style === "south" ? "is-active" : ""} aria-pressed={style === "south"} onClick={() => setStyle("south")}>South Indian</button>
    </div>
    {style === "north" ? <NorthIndianKundli houses={houses} planets={planets} /> : <SouthIndianKundli houses={houses} planets={planets} />}
  </div>;
}
