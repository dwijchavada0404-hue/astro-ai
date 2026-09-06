import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Profiles } from "./App";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

const source = {
  profile_id: "source-profile",
  label: "My chart",
  birth_date: "2000-04-04",
  birth_time: "14:04:00",
  place: "Borivali, Mumbai",
  is_default: true,
};

describe("birth profile correction workflow", () => {
  it("opens a prefilled in-app correction form", () => {
    render(<Profiles token="token" profiles={[source]} onCreated={vi.fn().mockResolvedValue(undefined)} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));

    expect(screen.getByRole("dialog", { name: /Duplicate & correct My chart/ })).toBeInTheDocument();
    expect(screen.getByLabelText("Corrected profile name")).toHaveValue("My chart (corrected)");
    expect(screen.getByLabelText("Corrected birth date")).toHaveValue("2000-04-04");
    expect(screen.getByLabelText("Corrected birth time")).toHaveValue("14:04");
    expect(screen.getByLabelText("Corrected birth place")).toHaveValue("Borivali, Mumbai");
    expect(screen.getByRole("button", { name: "Close correction form" })).toBeInTheDocument();
    expect(screen.getByText(/original profile and every conversation already linked to it stay unchanged/i)).toBeInTheDocument();
  });

  it("duplicates a profile before applying corrected birth details", async () => {
    const duplicate = {
      ...source,
      profile_id: "corrected-profile",
      label: "My chart corrected",
      is_default: false,
    };
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({ ok: true, status: 201, json: async () => ({ birth_profile: duplicate }) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ birth_profile: { ...duplicate, birth_time: "14:06:00" } }) });
    vi.stubGlobal("fetch", fetchMock);
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" profiles={[source]} onCreated={onCreated} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));
    fireEvent.change(screen.getByLabelText("Corrected profile name"), { target: { value: "My chart corrected" } });
    fireEvent.change(screen.getByLabelText("Corrected birth time"), { target: { value: "14:06" } });
    fireEvent.click(screen.getByRole("button", { name: "Save corrected copy" }));

    await waitFor(() => expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      expect.stringContaining("/api/v1/birth-profiles/source-profile/duplicate"),
      expect.objectContaining({ method: "POST", body: JSON.stringify({ label: "My chart corrected" }) }),
    ));
    await waitFor(() => expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      expect.stringContaining("/api/v1/birth-profiles/corrected-profile"),
      expect.objectContaining({ method: "PATCH", body: JSON.stringify({ date: "2000-04-04", time: "14:06", place: "Borivali, Mumbai" }) }),
    ));
    expect(onCreated).toHaveBeenCalled();
    await waitFor(() => expect(screen.queryByRole("dialog")).not.toBeInTheDocument());
  });

  it("does not create a duplicate when correction is cancelled", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);

    render(<Profiles token="token" profiles={[source]} onCreated={vi.fn().mockResolvedValue(undefined)} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));
    fireEvent.click(screen.getByRole("button", { name: "Cancel" }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(fetchMock).not.toHaveBeenCalled();
  });
});