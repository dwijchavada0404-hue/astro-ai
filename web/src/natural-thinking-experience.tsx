import { PropsWithChildren, useEffect } from "react";
import { createThinkingPlan } from "./thinking-experience";

const ASK_PATH = /\/api\/v1\/conversations\/[^/]+\/ask(?:\?|$)/;
const THINKING_SELECTOR = ".message.assistant.thinking > div";
function sleep(ms: number) { return new Promise<void>((resolve) => window.setTimeout(resolve, ms)); }
function setThinkingText(text: string) { const element = document.querySelector<HTMLElement>(THINKING_SELECTOR); if (element) element.textContent = `${text}…`; }

export function NaturalThinkingExperience({ children }: PropsWithChildren) {
  useEffect(() => {
    const originalFetch = window.fetch.bind(window);
    let active = true;
    window.fetch = async (input, init = {}) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      const method = (init.method || (input instanceof Request ? input.method : "GET")).toUpperCase();
      if (method !== "POST" || !ASK_PATH.test(url)) return originalFetch(input, init);
      let question = "";
      if (typeof init.body === "string") { try { question = String(JSON.parse(init.body)?.question || ""); } catch { /* API validates malformed input */ } }
      const plan = createThinkingPlan(question);
      const startedAt = performance.now();
      const responsePromise = originalFetch(input, init);
      await sleep(0);
      for (const step of plan.steps) { if (!active) break; setThinkingText(step.text); await sleep(step.durationMs); }
      const response = await responsePromise;
      const elapsed = performance.now() - startedAt;
      if (active && elapsed < plan.totalMs) await sleep(plan.totalMs - elapsed);
      return response;
    };
    return () => { active = false; window.fetch = originalFetch; };
  }, []);
  return <>{children}</>;
}
