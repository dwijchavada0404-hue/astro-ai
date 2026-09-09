import { ReactNode, useEffect, useState } from "react";

export type AnswerLanguage = "hinglish" | "english" | "hindi";

const STORAGE_KEY = "astroai.answer-language.v1";
const LANGUAGES: Array<{ value: AnswerLanguage; label: string }> = [
  { value: "hinglish", label: "Hinglish" },
  { value: "english", label: "English" },
  { value: "hindi", label: "हिंदी" },
];

export function loadAnswerLanguage(storage: Pick<Storage, "getItem"> = window.localStorage): AnswerLanguage {
  const saved = storage.getItem(STORAGE_KEY);
  return saved === "english" || saved === "hindi" || saved === "hinglish" ? saved : "hinglish";
}

export function withAnswerLanguage(body: BodyInit | null | undefined, language: AnswerLanguage): BodyInit | null | undefined {
  if (typeof body !== "string") return body;
  try {
    const value = JSON.parse(body) as Record<string, unknown>;
    if (typeof value.question !== "string") return body;
    return JSON.stringify({ ...value, answer_language: language });
  } catch {
    return body;
  }
}

export function AnswerLanguageExperience({ children }: { children: ReactNode }) {
  const [language, setLanguage] = useState<AnswerLanguage>(() => loadAnswerLanguage());

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, language);
  }, [language]);

  useEffect(() => {
    const originalFetch = window.fetch.bind(window);
    window.fetch = (input: RequestInfo | URL, init?: RequestInit) => {
      const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
      if (/\/api\/v1\/conversations\/[^/]+\/ask(?:\?|$)/.test(url) && init?.method?.toUpperCase() === "POST") {
        return originalFetch(input, { ...init, body: withAnswerLanguage(init.body, language) });
      }
      return originalFetch(input, init);
    };
    return () => { window.fetch = originalFetch; };
  }, [language]);

  return <>
    {children}
    <div className="answer-language-switcher" role="group" aria-label="Answer language">
      <span>Answer in</span>
      {LANGUAGES.map((item) => <button key={item.value} type="button" className={language === item.value ? "active" : ""} aria-pressed={language === item.value} onClick={() => setLanguage(item.value)}>{item.label}</button>)}
    </div>
  </>;
}
