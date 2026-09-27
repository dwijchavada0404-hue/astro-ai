import { describe, expect, it } from "vitest";

import { resolveFrontendRuntime } from "./runtime-config";

const production = {
  VITE_ASTROAI_ENVIRONMENT: "production",
  VITE_ASTROAI_API_URL: "https://api.astroai.example",
  VITE_OIDC_AUTHORITY: "https://tenant.example.com",
  VITE_OIDC_CLIENT_ID: "client-id",
  VITE_OIDC_AUDIENCE: "https://api.astroai.example",
};

describe("production frontend runtime", () => {
  it("accepts explicit HTTPS API and OIDC configuration", () => {
    const runtime = resolveFrontendRuntime(production);
    expect(runtime.environment).toBe("production");
    expect(runtime.apiUrl).toBe("https://api.astroai.example");
    expect(runtime.oidcAuthority).toBe("https://tenant.example.com");
    expect(runtime.oidcAudience).toBe("https://api.astroai.example");
  });

  it("fails closed when production variables are missing", () => {
    expect(() => resolveFrontendRuntime({ ...production, VITE_ASTROAI_API_URL: "" })).toThrow(/VITE_ASTROAI_API_URL/);
    expect(() => resolveFrontendRuntime({ ...production, VITE_OIDC_AUTHORITY: "" })).toThrow(/VITE_OIDC_AUTHORITY/);
    expect(() => resolveFrontendRuntime({ ...production, VITE_OIDC_CLIENT_ID: "" })).toThrow(/VITE_OIDC_CLIENT_ID/);
    expect(() => resolveFrontendRuntime({ ...production, VITE_OIDC_AUDIENCE: "" })).toThrow(/VITE_OIDC_AUDIENCE/);
  });

  it("rejects insecure or local production endpoints", () => {
    expect(() => resolveFrontendRuntime({ ...production, VITE_ASTROAI_API_URL: "http://api.example.com" })).toThrow(/HTTPS/);
    expect(() => resolveFrontendRuntime({ ...production, VITE_OIDC_AUTHORITY: "http://tenant.example.com" })).toThrow(/HTTPS/);
    expect(() => resolveFrontendRuntime({ ...production, VITE_ASTROAI_API_URL: "https://localhost:8000" })).toThrow(/localhost/);
  });

  it("fails closed for staging when the API URL is not configured", () => {
    expect(() => resolveFrontendRuntime({ VITE_ASTROAI_ENVIRONMENT: "staging" })).not.toThrow();
    const runtime = resolveFrontendRuntime({ VITE_ASTROAI_ENVIRONMENT: "staging" });
    expect(runtime.apiUrl).toBe("");
    expect(runtime.oidcAuthority).toBe("");
  });

  it("keeps local development on the local API by default", () => {
    const runtime = resolveFrontendRuntime({ VITE_ASTROAI_ENVIRONMENT: "development" });
    expect(runtime.apiUrl).toBe("http://127.0.0.1:8000");
  });
});
