import { UserManager, WebStorageStateStore, type User } from "oidc-client-ts";

import { frontendRuntime } from "./runtime-config";

export type AuthRuntime = {
  configured: boolean;
  manager: UserManager | null;
};

export function createAuthRuntime(): AuthRuntime {
  const authority = frontendRuntime.oidcAuthority;
  const clientId = frontendRuntime.oidcClientId;
  if (!authority || !clientId) return { configured: false, manager: null };

  const redirectUri = `${window.location.origin}/auth/callback`;
  const manager = new UserManager({
    authority,
    client_id: clientId,
    redirect_uri: redirectUri,
    post_logout_redirect_uri: window.location.origin,
    response_type: "code",
    scope: frontendRuntime.oidcScope,
    extraQueryParams: frontendRuntime.oidcAudience
      ? { audience: frontendRuntime.oidcAudience }
      : undefined,
    userStore: new WebStorageStateStore({ store: window.sessionStorage }),
    automaticSilentRenew: false,
  });
  return { configured: true, manager };
}

export function usableToken(user: User | null): string | null {
  if (!user || user.expired) return null;
  return user.access_token || null;
}
