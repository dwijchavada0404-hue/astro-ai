export type AnswerLanguage = "hinglish" | "english" | "hindi";

export const DEFAULT_ANSWER_LANGUAGE: AnswerLanguage = "hinglish";
export const ANSWER_LANGUAGE_STORAGE_KEY = "astroai.answerLanguage";

export const ANALYSIS_STEPS = [
  "Aapki kundli padh raha hoon…",
  "Planetary positions dekh raha hoon…",
  "Dasha periods analyse kar raha hoon…",
  "Timing indicators connect kar raha hoon…",
  "Aapki reading taiyaar kar raha hoon…",
] as const;

export function savedAnswerLanguage(): AnswerLanguage {
  try {
    const value = window.localStorage.getItem(ANSWER_LANGUAGE_STORAGE_KEY);
    return value === "english" || value === "hindi" || value === "hinglish" ? value : DEFAULT_ANSWER_LANGUAGE;
  } catch {
    return DEFAULT_ANSWER_LANGUAGE;
  }
}

export function saveAnswerLanguage(language: AnswerLanguage): void {
  try { window.localStorage.setItem(ANSWER_LANGUAGE_STORAGE_KEY, language); } catch { /* preference remains session-only */ }
}

export function analysisStep(elapsedMs: number): string {
  return ANALYSIS_STEPS[Math.min(Math.floor(elapsedMs / 650), ANALYSIS_STEPS.length - 1)];
}
