import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App, { Profiles } from "./App";

describe("AstroAI frontend foundation", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true }));
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
});
