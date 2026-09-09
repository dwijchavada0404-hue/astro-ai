import { describe, expect, it } from "vitest";
import { ANALYSIS_STEPS, DEFAULT_ANSWER_LANGUAGE, analysisStep } from "./answer-experience";

describe("answer experience", () => {
  it("defaults to Hinglish", () => expect(DEFAULT_ANSWER_LANGUAGE).toBe("hinglish"));
  it("progresses through chart analysis states", () => {
    expect(analysisStep(0)).toBe(ANALYSIS_STEPS[0]);
    expect(analysisStep(700)).toBe(ANALYSIS_STEPS[1]);
    expect(analysisStep(9999)).toBe(ANALYSIS_STEPS[ANALYSIS_STEPS.length - 1]);
  });
});
