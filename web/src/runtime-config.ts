export type FrontendRuntimeConfig = {
  environment: "development" | "staging" | "production";
  apiUrl: string;
  oidcAuthority: string;
  oidcClientId: string;
  oidcAudience: string;
  oidcScope: string;
};

type FrontendEnv = Record<string, string | undefined>;

const STAGING_API_FALLBACK = "https://astro-ai-production-54a7.up.railway.app";

function clean(value: string | undefined): string {
  return value?.trim() || "";
}

function requireHttps(name: string, value: string): void {
  if (!value.startsWith("https://")) {
    throw new Error(`${name} must use HTTPS in production.`);
  }
}

export function resolveFrontendRuntime(
  env: FrontendEnv,
): FrontendRuntimeConfig {
  const rawEnvironment = clean(env.VITE_ASTROAI_ENVIRONMENT) || "development";
  if (!(["development", "staging", "production"] as const).includes(rawEnvironment as never)) {
    throw new Error("VITE_ASTROAI_ENVIRONMENT must be development, staging, or production.");
  }
  const environment = rawEnvironment as FrontendRuntimeConfig["environment"];
  const production = environment === "production";

  const apiUrl = clean(env.VITE_ASTROAI_API_URL) || (production ? "" : STAGING_API_FALLBACK);
  const oidcAuthority = clean(env.VITE_OIDC_AUTHORITY);
  const oidcClientId = clean(env.VITE_OIDC_CLIENT_ID);
  const oidcAudience = clean(env.VITE_OIDC_AUDIENCE);
  const oidcScope = clean(env.VITE_OIDC_SCOPE) || "openid profile email";

  if (production) {
    if (!apiUrl) throw new Error("VITE_ASTROAI_API_URL is required in production.");
    if (!oidcAuthority) throw new Error("VITE_OIDC_AUTHORITY is required in production.");
    if (!oidcClientId) throw new Error("VITE_OIDC_CLIENT_ID is required in production.");
    if (!oidcAudience) throw new Error("VITE_OIDC_AUDIENCE is required in production.");
    requireHttps("VITE_ASTROAI_API_URL", apiUrl);
    requireHttps("VITE_OIDC_AUTHORITY", oidcAuthority);
    if (apiUrl.includes("localhost") || apiUrl.includes("127.0.0.1")) {
      throw new Error("Production API URL must not point to localhost.");
    }
    if (oidcAuthority.includes("localhost") || oidcAuthority.includes("127.0.0.1")) {
      throw new Error("Production OIDC authority must not point to localhost.");
    }
  }

  return {
    environment,
    apiUrl: apiUrl.replace(/\/$/, ""),
    oidcAuthority,
    oidcClientId,
    oidcAudience,
    oidcScope,
  };
}

export const frontendRuntime = resolveFrontendRuntime(import.meta.env);
