import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { Profiles } from "./App";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.unstubAllGlobals();
});

describe("birth profile correction workflow", () => {
  it("duplicates a profile before applying corrected birth details", async () => {
    const source = {
      profile_id: "source-profile",
      label: "My chart",
      birth_date: "2000-04-04",
      birth_time: "14:04:00",
      place: "Borivali, Mumbai",
      is_default: true,
    };
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
    vi.spyOn(window, "prompt")
      .mockReturnValueOnce("My chart corrected")
      .mockReturnValueOnce("2000-04-04")
      .mockReturnValueOnce("14:06")
      .mockReturnValueOnce("Borivali, Mumbai");
    const onCreated = vi.fn().mockResolvedValue(undefined);

    render(<Profiles token="token" profiles={[source]} onCreated={onCreated} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));

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
  });

  it("does not create a duplicate when correction is cancelled", () => {
    const fetchMock = vi.fn();
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "prompt").mockReturnValueOnce(null);

    render(<Profiles token="token" profiles={[{
      profile_id: "source-profile",
      label: "My chart",
      birth_date: "2000-04-04",
      birth_time: "14:04:00",
      place: "Borivali, Mumbai",
      is_default: true,
    }]} onCreated={vi.fn().mockResolvedValue(undefined)} />);
    fireEvent.click(screen.getByRole("button", { name: "Duplicate & correct" }));

    expect(fetchMock).not.toHaveBeenCalled();
  });
});
