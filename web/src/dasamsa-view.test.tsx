import { describe, expect, it } from "vitest";
import { dasamsaPlanetRows } from "./dasamsa-view";

describe("Dashamsha D10 viewer", () => {
  it("preserves backend D1 to D10 fields without recalculation", () => {
    expect(dasamsaPlanetRows({
      Sun: { d1_sign: "Aries", sign: "Gemini", house: 3, degree_dms: "10°00′00″" },
      Saturn: { d1_sign: "Gemini", sign: "Libra", house: 7, retrograde: true },
    })).toEqual([
      { name: "Sun", d1_sign: "Aries", sign: "Gemini", house: 3, degree_dms: "10°00′00″" },
      { name: "Saturn", d1_sign: "Gemini", sign: "Libra", house: 7, retrograde: true },
    ]);
  });

  it("handles absent D10 planets safely", () => {
    expect(dasamsaPlanetRows()).toEqual([]);
  });
});
