import { describe, expect, it } from "vitest";
import { kundliHouses } from "./kundli-chart";

describe("North Indian kundli chart", () => {
  it("maps engine signs and planets into the twelve houses without recalculation", () => {
    const rows = kundliHouses(
      { "1": { sign: "Leo", lord: "Sun" }, "7": { sign: "Aquarius", lord: "Saturn" } },
      { Sun: { house: 8, retrograde: false }, Saturn: { house: 7, retrograde: true }, Moon: { house: 1 } },
    );
    expect(rows).toHaveLength(12);
    expect(rows[0]).toEqual({ number: 1, sign: "Leo", lord: "Sun", planets: [{ name: "Moon", retrograde: false }] });
    expect(rows[6]).toEqual({ number: 7, sign: "Aquarius", lord: "Saturn", planets: [{ name: "Saturn", retrograde: true }] });
    expect(rows[7].planets).toEqual([{ name: "Sun", retrograde: false }]);
  });

  it("ignores invalid house numbers and safely fills missing engine house data", () => {
    const rows = kundliHouses(undefined, { Sun: { house: 13 }, Moon: {} });
    expect(rows.every((house) => house.planets.length === 0)).toBe(true);
    expect(rows[0].sign).toBe("—");
  });
});
