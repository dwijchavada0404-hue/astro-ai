import { describe, expect, it } from "vitest";
import { antardashaRows, currentDashaLabel, formatDegree, formatPeriodDate, mahadashaRows, planetRows } from "./chart-viewer";

describe("birth chart viewer", () => {
  it("prefers the deterministic DMS degree returned by the engine", () => {
    expect(formatDegree(12.3456, "12°20′44″")).toBe("12°20′44″");
    expect(formatDegree(12.3456)).toBe("12.35°");
    expect(formatDegree()).toBe("—");
  });

  it("preserves engine planet names and calculated fields", () => {
    expect(planetRows({
      Sun: { sign: "Pisces", house: 8, retrograde: false },
      Saturn: { sign: "Aries", house: 9, retrograde: true },
    })).toEqual([
      { name: "Sun", sign: "Pisces", house: 8, retrograde: false },
      { name: "Saturn", sign: "Aries", house: 9, retrograde: true },
    ]);
  });

  it("renders an empty planetary collection safely", () => {
    expect(planetRows()).toEqual([]);
  });

  it("formats deterministic Vimshottari periods without timezone shifting", () => {
    expect(formatPeriodDate("2026-09-06T20:45:00+05:30")).toBe("06 Sep 2026");
    expect(formatPeriodDate()).toBe("—");
    expect(formatPeriodDate("not-a-date")).toBe("—");
  });

  it("labels the current Mahadasha and Antardasha", () => {
    expect(currentDashaLabel({ mahadasha: "Venus", antardasha: "Mercury" })).toBe("Venus Mahadasha · Mercury Antardasha");
    expect(currentDashaLabel(null)).toBe("Current period unavailable");
  });

  it("preserves the engine Mahadasha sequence and marks the current period", () => {
    expect(mahadashaRows({
      current_period: { mahadasha: "Sun", antardasha: "Moon" },
      mahadashas: [
        { planet: "Venus", start: "2000-01-01", end: "2010-01-01" },
        { planet: "Sun", start: "2010-01-01", end: "2016-01-01" },
      ],
    })).toEqual([
      { planet: "Venus", start: "2000-01-01", end: "2010-01-01", isCurrent: false },
      { planet: "Sun", start: "2010-01-01", end: "2016-01-01", isCurrent: true },
    ]);
    expect(mahadashaRows()).toEqual([]);
  });

  it("preserves Antardasha order and only marks the active sub-period inside the current Mahadasha", () => {
    const current = { mahadasha: "Sun", antardasha: "Moon" };
    expect(antardashaRows({
      planet: "Sun",
      antardashas: [
        { planet: "Sun", start: "2010-01-01", end: "2010-05-01" },
        { planet: "Moon", start: "2010-05-01", end: "2010-11-01" },
      ],
    }, current)).toEqual([
      { planet: "Sun", start: "2010-01-01", end: "2010-05-01", isCurrent: false },
      { planet: "Moon", start: "2010-05-01", end: "2010-11-01", isCurrent: true },
    ]);
    expect(antardashaRows({ planet: "Venus", antardashas: [{ planet: "Moon" }] }, current)[0].isCurrent).toBe(false);
    expect(antardashaRows()).toEqual([]);
  });
});
