import { ChangeEvent } from "react";

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

export function persistAnswerLanguage(language: AnswerLanguage, storage: Pick<Storage, "setItem"> = window.localStorage) {
  storage.setItem(STORAGE_KEY, language);
}

export function AnswerLanguageSelector({ language, onChange }: { language: AnswerLanguage; onChange: (language: AnswerLanguage) => void }) {
  const selectLanguage = (event: ChangeEvent<HTMLSelectElement>) => onChange(event.target.value as AnswerLanguage);
  return <label className="answer-language-switcher">Answer in
    <select aria-label="Answer language" value={language} onChange={selectLanguage}>
      {LANGUAGES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
    </select>
  </label>;
}
