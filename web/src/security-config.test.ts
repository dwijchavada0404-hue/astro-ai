import { describe, expect, it } from "vitest";
import nginx from "../nginx.conf?raw";
import securityText from "../public/.well-known/security.txt?raw";
import headers from "../security-headers.conf?raw";


describe("frontend production security", () => {
  it("uses a restrictive CSP while allowing the live API and Auth0 authority", () => {
    expect(headers).toContain("default-src 'self'");
    expect(headers).toContain("object-src 'none'");
    expect(headers).toContain("frame-ancestors 'none'");
    expect(headers).toContain("https://astro-ai-production-54a7.up.railway.app");
    expect(headers).toContain("https://dev-q0zcg4qyan6zsd8w.eu.auth0.com");
    expect(headers).not.toMatch(/script-src[^;]*'unsafe-inline'/);
  });

  it("sets browser hardening and safe cache headers", () => {
    expect(headers).toContain("Strict-Transport-Security");
    expect(headers).toContain("Permissions-Policy");
    expect(headers).toContain("Cross-Origin-Opener-Policy");
    expect(nginx.match(/include \/etc\/nginx\/security-headers\.conf;/g)).toHaveLength(4);
    expect(nginx).toContain('Cache-Control "public, immutable"');
    expect(nginx).toContain('Cache-Control "no-cache"');
  });

  it("publishes a valid security contact with an expiry date", () => {
    expect(securityText).toMatch(/^Contact: https:\/\//m);
    expect(securityText).toMatch(/^Expires: 2027-08-30T00:00:00Z$/m);
    expect(securityText).toMatch(/^Canonical: https:\/\//m);
  });
});
