import { describe, expect, it } from "vitest";
import { formatDegree, planetRows } from "./chart-viewer";

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
});
