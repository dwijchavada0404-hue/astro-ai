import { PropsWithChildren, useEffect, useState } from "react";

export type BasicLifeContext = {
  relationshipStatus: "single" | "in_relationship" | "engaged" | "married" | "separated" | "divorced" | "widowed" | "prefer_not_to_say";
  hasChildren: "yes" | "no" | "prefer_not_to_say";
};

const STORAGE_KEY = "astroai.basic-life-context.v1";

export function lifeContextPayload(value: BasicLifeContext) {
  const milestones: Record<string, { state: string; note: string }> = {};
  if (["engaged", "married", "separated", "divorced", "widowed"].includes(value.relationshipStatus)) {
    milestones.committed_relationship = { state: "user_confirmed_achieved", note: `User-reported relationship status: ${value.relationshipStatus}.` };
  } else {
    milestones.committed_relationship = { state: "unknown", note: `User-reported relationship status: ${value.relationshipStatus}.` };
  }
  milestones.family_parenting = value.hasChildren === "yes"
    ? { state: "user_confirmed_achieved", note: "User reports having one or more children." }
    : { state: "unknown", note: value.hasChildren === "no" ? "User reports no children." : "User preferred not to provide children context." };
  return { milestones };
}

function storedContext(): BasicLifeContext | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    const value = JSON.parse(raw) as BasicLifeContext;
    return value?.relationshipStatus && value?.hasChildren ? value : null;
  } catch { return null; }
}

export function LifeContextOnboarding({ children }: PropsWithChildren) {
  const [show, setShow] = useState(false);
  const [relationshipStatus, setRelationshipStatus] = useState<BasicLifeContext["relationshipStatus"]>("single");
  const [hasChildren, setHasChildren] = useState<BasicLifeContext["hasChildren"]>("no");

  useEffect(() => {
    const originalFetch = window.fetch.bind(window);
    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      const headers = new Headers(init.headers || (input instanceof Request ? input.headers : undefined));
      const authenticated = headers.has("Authorization");
      if (authenticated && !storedContext() && url.includes("/api/v1/birth-profiles")) setShow(true);

      if (authenticated && url.endsWith("/api/v1/conversations") && (init.method || "GET").toUpperCase() === "POST") {
        const context = storedContext();
        if (context && typeof init.body === "string") {
          try {
            const body = JSON.parse(init.body);
            if (!body.life_context) init = { ...init, body: JSON.stringify({ ...body, life_context: lifeContextPayload(context) }) };
          } catch { /* leave malformed payload to the API */ }
        }
      }
      return originalFetch(input, init);
    };
    return () => { window.fetch = originalFetch; };
  }, []);

  const save = () => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ relationshipStatus, hasChildren } satisfies BasicLifeContext));
    setShow(false);
  };

  return <>
    {children}
    {show && <div role="dialog" aria-modal="true" aria-labelledby="life-context-title" style={{ position: "fixed", inset: 0, zIndex: 1000, background: "rgba(7,9,20,.72)", display: "grid", placeItems: "center", padding: 20 }}>
      <section style={{ width: "min(520px, 100%)", background: "#fff", color: "#171526", borderRadius: 20, padding: 28, boxShadow: "0 24px 80px rgba(0,0,0,.35)" }}>
        <div className="eyebrow">A little real-life context</div>
        <h2 id="life-context-title">Help AstroAI understand where you are today</h2>
        <p>This prevents the chart from predicting milestones that have already happened. You can choose “Prefer not to say”.</p>
        <label style={{ display: "grid", gap: 8, marginTop: 18 }}>Relationship status
          <select aria-label="Relationship status" value={relationshipStatus} onChange={(e) => setRelationshipStatus(e.target.value as BasicLifeContext["relationshipStatus"])} style={{ padding: 12, borderRadius: 10 }}>
            <option value="single">Single</option><option value="in_relationship">In a relationship</option><option value="engaged">Engaged</option><option value="married">Married</option><option value="separated">Separated</option><option value="divorced">Divorced</option><option value="widowed">Widowed</option><option value="prefer_not_to_say">Prefer not to say</option>
          </select>
        </label>
        <label style={{ display: "grid", gap: 8, marginTop: 18 }}>Do you have children?
          <select aria-label="Children status" value={hasChildren} onChange={(e) => setHasChildren(e.target.value as BasicLifeContext["hasChildren"])} style={{ padding: 12, borderRadius: 10 }}>
            <option value="no">No</option><option value="yes">Yes</option><option value="prefer_not_to_say">Prefer not to say</option>
          </select>
        </label>
        <button className="primary" type="button" onClick={save} style={{ marginTop: 24 }}>Save and continue →</button>
        <p style={{ fontSize: 12, opacity: .7, marginTop: 14 }}>These answers are user-provided context only. AstroAI does not infer marital or parenting status from your birth chart.</p>
      </section>
    </div>}
  </>;
}
