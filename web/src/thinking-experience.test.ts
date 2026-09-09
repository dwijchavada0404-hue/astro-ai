import { describe, expect, it } from "vitest";
import { createThinkingPlan, detectThinkingDomain } from "./thinking-experience";

describe("thinking experience", () => {
  it("detects question domains including Hinglish", () => {
    expect(detectThinkingDomain("meri shaadi kab hogi")).toBe("marriage");
    expect(detectThinkingDomain("mera pehla bacha kab hoga")).toBe("family_children");
    expect(detectThinkingDomain("When will I buy my first home?")).toBe("property_home");
    expect(detectThinkingDomain("foreign travel kab hoga")).toBe("travel");
  });

  it("keeps the total presentation plan within seven seconds", () => {
    const values = [0.9, 0.1, 0.8, 0.2, 0.7, 0.3, 0.6, 0.4, 0.5, 0.9, 0.1, 0.8];
    let index = 0;
    const plan = createThinkingPlan("meri shaadi kab hogi", () => values[index++ % values.length]);
    expect(plan.steps.length).toBeGreaterThanOrEqual(3);
    expect(plan.steps.length).toBeLessThanOrEqual(4);
    expect(plan.totalMs).toBeLessThanOrEqual(7000);
    expect(plan.steps.every((step) => step.durationMs >= 700)).toBe(true);
  });

  it("varies plans when the random sequence changes", () => {
    const first = createThinkingPlan("career kaisa rahega", () => 0.1);
    const second = createThinkingPlan("career kaisa rahega", () => 0.9);
    expect(first.steps.map((step) => step.text)).not.toEqual(second.steps.map((step) => step.text));
  });
});
