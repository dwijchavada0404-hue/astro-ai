import { describe, expect, it } from "vitest";
import { navamsaPlanetRows } from "./navamsa-view";

describe("Navamsa D9 viewer", () => {
  it("preserves backend D1 to D9 comparison fields without recalculation", () => {
    expect(navamsaPlanetRows({
      Venus: { d1_sign: "Taurus", sign: "Taurus", house: 2, vargottama: true },
      Saturn: { d1_sign: "Gemini", sign: "Libra", house: 7, retrograde: true, vargottama: false },
    })).toEqual([
      { name: "Venus", d1_sign: "Taurus", sign: "Taurus", house: 2, vargottama: true },
      { name: "Saturn", d1_sign: "Gemini", sign: "Libra", house: 7, retrograde: true, vargottama: false },
    ]);
  });

  it("handles an absent D9 planet collection safely", () => {
    expect(navamsaPlanetRows()).toEqual([]);
  });
});
