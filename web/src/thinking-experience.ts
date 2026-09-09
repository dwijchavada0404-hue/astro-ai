export type ThinkingDomain =
  | "marriage"
  | "family_children"
  | "career"
  | "finance"
  | "property_home"
  | "travel"
  | "general";

export type ThinkingStep = { text: string; durationMs: number };
export type ThinkingPlan = { domain: ThinkingDomain; steps: ThinkingStep[]; totalMs: number };

const MESSAGES: Record<ThinkingDomain, readonly string[]> = {
  marriage: [
    "Aapke relationship indicators dekh raha hoon…",
    "7th house aur marriage yog analyse kar raha hoon…",
    "Dasha timing ko marriage signals se match kar raha hoon…",
    "Relationship pattern ko final reading mein combine kar raha hoon…",
  ],
  family_children: [
    "Family aur parenting indicators dekh raha hoon…",
    "5th house ke themes analyse kar raha hoon…",
    "Relevant dasha periods compare kar raha hoon…",
    "Family timing signals ko combine kar raha hoon…",
  ],
  career: [
    "Career houses aur strengths dekh raha hoon…",
    "Professional yog analyse kar raha hoon…",
    "Current dasha ko career timing se match kar raha hoon…",
    "Career direction ke strongest signals combine kar raha hoon…",
  ],
  finance: [
    "Wealth aur income indicators dekh raha hoon…",
    "Financial houses aur planetary support analyse kar raha hoon…",
    "Dasha timing ko money themes se match kar raha hoon…",
    "Financial pattern ki final reading bana raha hoon…",
  ],
  property_home: [
    "Home aur property indicators dekh raha hoon…",
    "4th house ke signals analyse kar raha hoon…",
    "Property timing ke dasha periods compare kar raha hoon…",
    "Past aur upcoming property windows combine kar raha hoon…",
  ],
  travel: [
    "Travel aur foreign connection indicators dekh raha hoon…",
    "Long-distance movement ke yog analyse kar raha hoon…",
    "Dasha timing ko travel signals se match kar raha hoon…",
    "Strongest travel windows combine kar raha hoon…",
  ],
  general: [
    "Aapki kundli ke relevant factors dekh raha hoon…",
    "Planetary patterns analyse kar raha hoon…",
    "Current dasha aur timing signals compare kar raha hoon…",
    "Reading ke strongest indicators combine kar raha hoon…",
  ],
};

export function detectThinkingDomain(question: string): ThinkingDomain {
  const q = question.trim().toLowerCase();
  if (/shaadi|shadi|marriage|marry|spouse|husband|wife|relationship|love|arranged/.test(q)) return "marriage";
  if (/bacha|baccha|bachcha|child|children|kid|kids|parent|family/.test(q)) return "family_children";
  if (/career|job|profession|promotion|business|work/.test(q)) return "career";
  if (/finance|money|wealth|income|salary|financial|paisa/.test(q)) return "finance";
  if (/property|home|house|ghar|flat/.test(q)) return "property_home";
  if (/travel|foreign|abroad|overseas|relocat|settle/.test(q)) return "travel";
  return "general";
}

function shuffled<T>(items: readonly T[], random: () => number): T[] {
  const values = [...items];
  for (let i = values.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [values[i], values[j]] = [values[j], values[i]];
  }
  return values;
}

export function createThinkingPlan(question: string, random: () => number = Math.random): ThinkingPlan {
  const domain = detectThinkingDomain(question);
  // Keep the experience short: 3–4 truthful presentation stages, capped at 7s.
  const stepCount = random() < 0.5 ? 3 : 4;
  const texts = shuffled(MESSAGES[domain], random).slice(0, stepCount);
  const durations = texts.map(() => 900 + Math.floor(random() * 1201)); // 0.9s–2.1s each.
  const rawTotal = durations.reduce((sum, value) => sum + value, 0);
  const targetTotal = 5000 + Math.floor(random() * 2001); // 5–7s overall target.
  const scale = rawTotal > targetTotal ? targetTotal / rawTotal : 1;
  const adjusted = durations.map((value) => Math.max(700, Math.round(value * scale)));
  return {
    domain,
    steps: texts.map((text, index) => ({ text, durationMs: adjusted[index] })),
    totalMs: adjusted.reduce((sum, value) => sum + value, 0),
  };
}
