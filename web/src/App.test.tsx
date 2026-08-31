import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "oidc-client-ts";
import App, { LegalDocument, Profiles, Workspace, conversationTitle, legalPageFromPath, shouldSubmitQuestion, tokenExpiryDelay } from "./App";

describe("AstroAI frontend foundation", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders the evidence-led landing experience when OIDC is not configured", async () => {
    render(<App />);
    await waitFor(() => expect(screen.getByText("API online")).toBeInTheDocument());
    expect(screen.getByRole("heading", { name: /Your chart.*Your questions.*Clearer direction/i })).toBeInTheDocument();
    expect(screen.getByText("Calculated first")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Begin your reading/ })).toBeDisabled();
    expect(screen.getByRole("link", { name: "Privacy" })).toHaveAttribute("href", "/privacy");
    expect(screen.getByRole("link", { name: "Source (AGPL-3.0)" })).toHaveAttribute(
      "href",
      "https://github.com/dwijchavada0404-hue/astro-ai",
    );
  });

  it("maps only supported public legal routes", () => {
    expect(legalPageFromPath("/privacy")).toBe("privacy");
    expect(legalPageFromPath("/terms/")).toBe("terms");
    expect(legalPageFromPath("/disclaimer")).toBe("disclaimer");
    expect(legalPageFromPath("/auth/callback")).toBeNull();
  });

  it("renders privacy, terms and safety content without authentication", () => {
    const { rerender } = render(<LegalDocument page="privacy" />);
    expect(screen.getByRole("heading", { name: "Privacy Notice" })).toBeInTheDocument();
    expect(screen.getByText(/Railway in the EU region/)).toBeInTheDocument();
    rerender(<LegalDocument page="terms" />);
    expect(screen.getByRole("heading", { name: "Terms of Use" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Free software licence" })).toBeInTheDocument();
    rerender(<LegalDocument page="disclaimer" />);
    expect(screen.getByRole("heading", { name: "Astrology & Safety Disclaimer" })).toBeInTheDocument();
    expect(screen.getByText(/No guaranteed outcomes/)).toBeInTheDocument();
  });

  it("lets a user choose another saved chart as the default", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" onCreated={onCreated} profiles={[
      { profile_id: "default", label: "My chart", birth_date: "2000-04-04", birth_time: "14:04:00", place: "Mumbai", is_default: true },
      { profile_id: "partner", label: "Partner chart", birth_date: "2001-05-05", birth_time: "09:30:00", place: "Pune", is_default: false },
    ]} />);

    fireEvent.click(screen.getByRole("button", { name: "Make default" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/birth-profiles/partner"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ is_default: true }) }),
    ));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("deletes an unused birth profile after confirmation", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "confirm").mockReturnValue(true);
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" onCreated={onCreated} profiles={[
      { profile_id: "unused", label: "Old chart", birth_date: "2000-04-04", birth_time: "14:04:00", place: "Mumbai", is_default: true },
    ]} />);
    fireEvent.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/birth-profiles/unused"),
      expect.objectContaining({ method: "DELETE" }),
    ));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("renames a birth profile without changing its birth data", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => ({}) });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "prompt").mockReturnValue("  Partner's   chart  ");
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" onCreated={onCreated} profiles={[
      { profile_id: "partner", label: "Old label", birth_date: "2001-05-05", birth_time: "09:30:00", place: "Pune", is_default: false },
    ]} />);
    fireEvent.click(screen.getByRole("button", { name: "Rename" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/birth-profiles/partner"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ label: "Partner's chart" }) }),
    ));
    await waitFor(() => expect(onCreated).toHaveBeenCalled());
  });

  it("deletes all AstroAI data only after typed confirmation", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, status: 204 });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "prompt").mockReturnValue("DELETE");
    const onDataDeleted = vi.fn();

    render(<Profiles token="token" profiles={[]} onCreated={vi.fn().mockResolvedValue(undefined)} onDataDeleted={onDataDeleted} />);
    fireEvent.click(screen.getByRole("button", { name: "Delete all AstroAI data" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/profile"),
      expect.objectContaining({ method: "DELETE" }),
    ));
    await waitFor(() => expect(onDataDeleted).toHaveBeenCalled());
  });

  it("exports a portable copy of the authenticated user's data", async () => {
    const fetchMock = vi.fn().mockResolvedValue({ ok: true, blob: async () => new Blob(["{}"], { type: "application/json" }) });
    vi.stubGlobal("fetch", fetchMock);
    const createObjectURL = vi.fn().mockReturnValue("blob:astroai-export");
    const revokeObjectURL = vi.fn();
    vi.stubGlobal("URL", { createObjectURL, revokeObjectURL });
    const click = vi.spyOn(HTMLAnchorElement.prototype, "click").mockImplementation(() => {});

    render(<Profiles token="token" profiles={[]} onCreated={vi.fn().mockResolvedValue(undefined)} onDataDeleted={vi.fn()} />);
    fireEvent.click(screen.getByRole("button", { name: "Export my data" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/profile/export"),
      expect.objectContaining({ headers: { Authorization: "Bearer token" } }),
    ));
    expect(createObjectURL).toHaveBeenCalled();
    expect(click).toHaveBeenCalled();
    expect(revokeObjectURL).toHaveBeenCalledWith("blob:astroai-export");
  });

  it("creates a concise conversation title from the first question", () => {
    expect(conversationTitle("  When   will I change my career?  ")).toBe("When will I change my career?");
    expect(conversationTitle("What does my chart suggest about a major international career move during the next three years?")).toHaveLength(50);
    expect(conversationTitle("What does my chart suggest about a major international career move during the next three years?")).toMatch(/…$/);
  });

  it("uses Enter to send while preserving Shift+Enter for a new line", () => {
    expect(shouldSubmitQuestion("Enter", false)).toBe(true);
    expect(shouldSubmitQuestion("Enter", true)).toBe(false);
    expect(shouldSubmitQuestion("a", false)).toBe(false);
  });

  it("calculates when an authenticated session must expire", () => {
    expect(tokenExpiryDelay(undefined, 1_000)).toBeNull();
    expect(tokenExpiryDelay(10, 4_000)).toBe(6_000);
    expect(tokenExpiryDelay(10, 12_000)).toBe(0);
  });

  it("deletes a conversation only after confirmation", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: [] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [{ conversation_id: "chat-1", title: "Career timing", birth_profile_id: "profile-1" }] }) })
      .mockResolvedValueOnce({ ok: true, status: 204 });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    await screen.findByRole("button", { name: "Career timing" });
    fireEvent.click(screen.getByRole("button", { name: "Delete Career timing" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/conversations/chat-1"),
      expect.objectContaining({ method: "DELETE" }),
    ));
    await waitFor(() => expect(screen.queryByRole("button", { name: "Career timing" })).not.toBeInTheDocument());
  });

  it("renames a saved conversation", async () => {
    const renamed = { conversation_id: "chat-1", title: "Next career move", birth_profile_id: "profile-1" };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: [] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [{ conversation_id: "chat-1", title: "Career timing", birth_profile_id: "profile-1" }] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversation: renamed }) });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "prompt").mockReturnValue("  Next   career move  ");

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    await screen.findByRole("button", { name: "Career timing" });
    fireEvent.click(screen.getByRole("button", { name: "Rename Career timing" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/conversations/chat-1"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ title: "Next career move" }) }),
    ));
    expect(await screen.findByRole("button", { name: "Next career move" })).toBeInTheDocument();
  });

  it("keeps workspace navigation available on mobile", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: [] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [] }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    const open = screen.getByRole("button", { name: "Open navigation" });
    fireEvent.click(open);

    expect(open).toHaveAttribute("aria-expanded", "true");
    expect(screen.getByLabelText("Workspace navigation")).toHaveClass("mobile-open");
    fireEvent.click(screen.getByRole("button", { name: /Birth profiles/ }));

    expect(screen.getByRole("heading", { name: "Birth profiles" })).toBeInTheDocument();
    expect(open).toHaveAttribute("aria-expanded", "false");
  });

  it("starts a conversation with the chart selected by the user", async () => {
    const profiles = [
      { profile_id: "mine", label: "My chart", birth_date: "2000-04-04", birth_time: "14:04:00", place: "Mumbai", is_default: true },
      { profile_id: "partner", label: "Partner chart", birth_date: "2001-05-05", birth_time: "09:30:00", place: "Pune", is_default: false },
    ];
    const created = { conversation_id: "chat-partner", title: "New conversation", birth_profile_id: "partner" };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: profiles }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [] }) })
      .mockResolvedValueOnce({ ok: true, status: 201, json: async () => ({ conversation: created }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    const picker = await screen.findByRole("combobox", { name: "Chart for this conversation" });
    expect(picker).toHaveValue("mine");
    fireEvent.change(picker, { target: { value: "partner" } });
    fireEvent.click(screen.getByRole("button", { name: "Start asking" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/conversations"),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ title: "New conversation", birth_profile_id: "partner" }) }),
    ));
  });

  it("shows the birth chart linked to a reopened conversation", async () => {
    const profile = { profile_id: "partner", label: "Partner chart", birth_date: "2001-05-05", birth_time: "09:30:00", place: "Pune", is_default: false };
    const conversation = { conversation_id: "chat-1", title: "Relationship timing", birth_profile_id: "partner" };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: [profile] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [conversation] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversation, messages: [] }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button", { name: "Relationship timing" }));

    expect(await screen.findByLabelText("Active birth profile")).toHaveTextContent("Partner chart");
  });

  it("copies an assistant answer to the clipboard", async () => {
    const profile = { profile_id: "mine", label: "My chart", birth_date: "2000-04-04", birth_time: "14:04:00", place: "Mumbai", is_default: true };
    const conversation = { conversation_id: "chat-1", title: "Career timing", birth_profile_id: "mine" };
    const answer = { message_id: "answer-1", role: "assistant" as const, content: "A supportive career period begins next year.", domain: "career" };
    const writeText = vi.fn().mockResolvedValue(undefined);
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profiles: [profile] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversations: [conversation] }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ conversation, messages: [answer] }) });
    vi.stubGlobal("fetch", fetchMock);

    render(<Workspace token="token" user={{ profile: { name: "Dwij" } } as User} onSignOut={vi.fn()} />);
    fireEvent.click(await screen.findByRole("button", { name: "Career timing" }));
    fireEvent.click(await screen.findByRole("button", { name: "Copy answer" }));

    await waitFor(() => expect(writeText).toHaveBeenCalledWith(answer.content));
    expect(screen.getByRole("button", { name: "Copy answer" })).toHaveTextContent("Copied");
  });
});
