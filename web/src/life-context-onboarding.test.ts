import { describe, expect, it } from "vitest";
import { lifeContextPayload } from "./life-context-onboarding";

describe("basic life context onboarding", () => {
  it("marks marriage and parenting as user-confirmed facts", () => {
    const result = lifeContextPayload({ relationshipStatus: "married", hasChildren: "yes" });
    expect(result.milestones.committed_relationship.state).toBe("user_confirmed_achieved");
    expect(result.milestones.family_parenting.state).toBe("user_confirmed_achieved");
  });

  it("does not convert single/no-children answers into predicted facts", () => {
    const result = lifeContextPayload({ relationshipStatus: "single", hasChildren: "no" });
    expect(result.milestones.committed_relationship.state).toBe("unknown");
    expect(result.milestones.family_parenting.state).toBe("unknown");
  });

  it("keeps prefer-not-to-say non-factual", () => {
    const result = lifeContextPayload({ relationshipStatus: "prefer_not_to_say", hasChildren: "prefer_not_to_say" });
    expect(result.milestones.committed_relationship.state).toBe("unknown");
    expect(result.milestones.family_parenting.state).toBe("unknown");
  });
});
