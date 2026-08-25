import { render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App";

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
});
