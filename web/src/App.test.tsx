import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "oidc-client-ts";
import App, { Profiles, Workspace, conversationTitle } from "./App";

describe("AstroAI frontend foundation", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("renders the evidence-led landing experience when OIDC is not configured", async () => {
    render(<App />);
    await waitFor(() => expect(screen.getByText("API online")).toBeInTheDocument());
    expect(screen.getByRole("heading", { name: /Your chart.*Your questions.*Clearer direction/i })).toBeInTheDocument();
    expect(screen.getByText("Calculated first")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Begin your reading/ })).toBeDisabled();
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

  it("creates a concise conversation title from the first question", () => {
    expect(conversationTitle("  When   will I change my career?  ")).toBe("When will I change my career?");
    expect(conversationTitle("What does my chart suggest about a major international career move during the next three years?")).toHaveLength(50);
    expect(conversationTitle("What does my chart suggest about a major international career move during the next three years?")).toMatch(/…$/);
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
});
