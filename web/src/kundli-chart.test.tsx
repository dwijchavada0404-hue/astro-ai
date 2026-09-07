import { describe, expect, it } from "vitest";
import { kundliHouses, SOUTH_INDIAN_SIGNS, southIndianCells } from "./kundli-chart";

describe("kundli chart mappings", () => {
  it("maps engine signs and planets into the twelve North Indian houses without recalculation", () => {
    const rows = kundliHouses(
      { "1": { sign: "Leo", lord: "Sun" }, "7": { sign: "Aquarius", lord: "Saturn" } },
      { Sun: { house: 8, retrograde: false }, Saturn: { house: 7, retrograde: true }, Moon: { house: 1 } },
    );
    expect(rows).toHaveLength(12);
    expect(rows[0]).toEqual({ number: 1, sign: "Leo", lord: "Sun", planets: [{ name: "Moon", retrograde: false, degree: undefined, nakshatra: undefined }] });
    expect(rows[6]).toEqual({ number: 7, sign: "Aquarius", lord: "Saturn", planets: [{ name: "Saturn", retrograde: true, degree: undefined, nakshatra: undefined }] });
    expect(rows[7].planets).toEqual([{ name: "Sun", retrograde: false, degree: undefined, nakshatra: undefined }]);
  });

  it("preserves engine degree and nakshatra details for the selected-house inspector", () => {
    const rows = kundliHouses(
      { "5": { sign: "Sagittarius", lord: "Jupiter" } },
      { Jupiter: { house: 5, retrograde: true, degree_dms: "14°22′10″", nakshatra: "Purva Ashadha" } },
    );
    expect(rows[4]).toEqual({ number: 5, sign: "Sagittarius", lord: "Jupiter", planets: [{ name: "Jupiter", retrograde: true, degree: "14°22′10″", nakshatra: "Purva Ashadha" }] });
  });

  it("ignores invalid North Indian house numbers and safely fills missing engine house data", () => {
    const rows = kundliHouses(undefined, { Sun: { house: 13 }, Moon: {} });
    expect(rows.every((house) => house.planets.length === 0)).toBe(true);
    expect(rows[0].sign).toBe("—");
  });

  it("keeps traditional South Indian zodiac signs in fixed clockwise positions", () => {
    expect(SOUTH_INDIAN_SIGNS).toEqual([
      "Pisces", "Aries", "Taurus", "Gemini", "Cancer", "Leo",
      "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius",
    ]);
  });

  it("maps backend house, lord and planet detail data into fixed South Indian sign cells", () => {
    const cells = southIndianCells(
      { "1": { sign: "Leo", lord: "Sun" }, "2": { sign: "Virgo", lord: "Mercury" }, "7": { sign: "Aquarius", lord: "Saturn" } },
      {
        Sun: { sign: "Virgo", house: 2, degree_dms: "18°10′00″", nakshatra: "Hasta" },
        Moon: { sign: "Leo", house: 1 },
        Saturn: { sign: "Aquarius", house: 7, retrograde: true, degree_dms: "04°03′02″", nakshatra: "Dhanishta" },
      },
    );
    expect(cells).toHaveLength(12);
    expect(cells.find((cell) => cell.sign === "Leo")).toEqual({ sign: "Leo", houseNumber: 1, lord: "Sun", planets: [{ name: "Moon", retrograde: false, degree: undefined, nakshatra: undefined }] });
    expect(cells.find((cell) => cell.sign === "Virgo")).toEqual({ sign: "Virgo", houseNumber: 2, lord: "Mercury", planets: [{ name: "Sun", retrograde: false, degree: "18°10′00″", nakshatra: "Hasta" }] });
    expect(cells.find((cell) => cell.sign === "Aquarius")).toEqual({ sign: "Aquarius", houseNumber: 7, lord: "Saturn", planets: [{ name: "Saturn", retrograde: true, degree: "04°03′02″", nakshatra: "Dhanishta" }] });
  });

  it("falls back to the backend house sign when a planet sign is omitted", () => {
    const cells = southIndianCells({ "1": { sign: "Aries", lord: "Mars" } }, { Moon: { house: 1 } });
    expect(cells.find((cell) => cell.sign === "Aries")?.planets).toEqual([{ name: "Moon", retrograde: false, degree: undefined, nakshatra: undefined }]);
  });

  it("keeps unmapped South Indian cells safe for inspection", () => {
    const cells = southIndianCells();
    expect(cells[0]).toEqual({ sign: "Pisces", houseNumber: undefined, lord: "—", planets: [] });
  });
});
