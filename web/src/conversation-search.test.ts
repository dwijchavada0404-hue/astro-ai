import { describe, expect, it } from "vitest";
import type { Conversation } from "./api";
import { filterConversations } from "./App";

const conversations: Conversation[] = [
  { conversation_id: "c1", title: "Career timing 2027", birth_profile_id: "p1" },
  { conversation_id: "c2", title: "Marriage and relationships", birth_profile_id: "p1" },
  { conversation_id: "c3", title: "Financial growth outlook", birth_profile_id: "p2" },
];

describe("filterConversations", () => {
  it("returns every conversation for an empty query", () => {
    expect(filterConversations(conversations, "   ")).toEqual(conversations);
  });

  it("matches conversation titles case-insensitively", () => {
    expect(filterConversations(conversations, "CAREER").map((item) => item.conversation_id)).toEqual(["c1"]);
    expect(filterConversations(conversations, "relationships").map((item) => item.conversation_id)).toEqual(["c2"]);
  });

  it("normalizes extra query whitespace and preserves original ordering", () => {
    const matching: Conversation[] = [
      { conversation_id: "c4", title: "Career and finance planning", birth_profile_id: "p1" },
      { conversation_id: "c5", title: "Career and finance review", birth_profile_id: "p2" },
    ];
    expect(filterConversations(matching, "  career   and finance ").map((item) => item.conversation_id)).toEqual(["c4", "c5"]);
  });

  it("returns an empty list when nothing matches", () => {
    expect(filterConversations(conversations, "health")).toEqual([]);
  });
});
