import { describe, expect, it } from "vitest";
import { lifeContextPayload } from "./life-context-onboarding";

describe("basic life context onboarding", () => {
  it("marks marriage parenting and home ownership as user-confirmed facts", () => {
    const result = lifeContextPayload({ relationshipStatus:"married", hasChildren:"yes", ownsHome:"yes", homeAchievedMonth:"2025-12" });
    expect(result.milestones.committed_relationship.state).toBe("user_confirmed_achieved");
    expect(result.milestones.family_parenting.state).toBe("user_confirmed_achieved");
    expect(result.milestones.home_property.state).toBe("user_confirmed_achieved");
    expect(result.milestones.home_property.achieved_date).toBe("2025-12");
  });

  it("does not convert pending answers into predicted facts", () => {
    const result = lifeContextPayload({ relationshipStatus:"single", hasChildren:"no", ownsHome:"no" });
    expect(result.milestones.committed_relationship.state).toBe("unknown");
    expect(result.milestones.family_parenting.state).toBe("unknown");
    expect(result.milestones.home_property.state).toBe("unknown");
  });

  it("keeps prefer-not-to-say non-factual", () => {
    const result = lifeContextPayload({ relationshipStatus:"prefer_not_to_say", hasChildren:"prefer_not_to_say", ownsHome:"prefer_not_to_say" });
    expect(result.milestones.committed_relationship.state).toBe("unknown");
    expect(result.milestones.family_parenting.state).toBe("unknown");
    expect(result.milestones.home_property.state).toBe("unknown");
  });
});
