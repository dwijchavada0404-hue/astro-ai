import { describe, expect, it } from "vitest";
import { parseAstroAiBackup } from "./backup";

describe("parseAstroAiBackup", () => {
  it("accepts an AstroAI export v1 object", () => {
    const backup = parseAstroAiBackup(JSON.stringify({ export_version: 1, birth_profiles: [], conversations: [] }));
    expect(backup.export_version).toBe(1);
  });

  it("rejects malformed JSON", () => {
    expect(() => parseAstroAiBackup("{not-json")).toThrow("not valid JSON");
  });

  it("rejects unsupported export versions", () => {
    expect(() => parseAstroAiBackup(JSON.stringify({ export_version: 2 }))).toThrow("export version 1");
  });

  it("rejects invalid collection shapes", () => {
    expect(() => parseAstroAiBackup(JSON.stringify({ export_version: 1, conversations: {} }))).toThrow("invalid conversations");
  });
});
