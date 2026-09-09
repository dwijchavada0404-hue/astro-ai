import { describe, expect, it } from "vitest";
import { loadAnswerLanguage, withAnswerLanguage } from "./answer-language";

describe("answer language", () => {
  it("defaults to Hinglish", () => {
    expect(loadAnswerLanguage({ getItem: () => null })).toBe("hinglish");
  });

  it("restores a valid saved preference", () => {
    expect(loadAnswerLanguage({ getItem: () => "english" })).toBe("english");
    expect(loadAnswerLanguage({ getItem: () => "hindi" })).toBe("hindi");
  });

  it("ignores an invalid saved preference", () => {
    expect(loadAnswerLanguage({ getItem: () => "klingon" })).toBe("hinglish");
  });

  it("injects the selected language into ask payloads", () => {
    const body = withAnswerLanguage(JSON.stringify({ question: "Meri job change kab hogi", reference_moment: "2026-09-09T12:00:00Z" }), "hindi");
    expect(JSON.parse(String(body))).toMatchObject({ question: "Meri job change kab hogi", answer_language: "hindi" });
  });

  it("does not alter unrelated JSON payloads", () => {
    const body = JSON.stringify({ title: "New conversation" });
    expect(withAnswerLanguage(body, "english")).toBe(body);
  });
});
