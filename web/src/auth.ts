import { UserManager, WebStorageStateStore, type User } from "oidc-client-ts";

export type AuthRuntime = {
  configured: boolean;
  manager: UserManager | null;
};

export function createAuthRuntime(): AuthRuntime {
  const authority = import.meta.env.VITE_OIDC_AUTHORITY?.trim();
  const clientId = import.meta.env.VITE_OIDC_CLIENT_ID?.trim();
  if (!authority || !clientId) return { configured: false, manager: null };

  const redirectUri = `${window.location.origin}/auth/callback`;
  const manager = new UserManager({
    authority,
    client_id: clientId,
    redirect_uri: redirectUri,
    post_logout_redirect_uri: window.location.origin,
    response_type: "code",
    scope: import.meta.env.VITE_OIDC_SCOPE || "openid profile email",
    extraQueryParams: import.meta.env.VITE_OIDC_AUDIENCE
      ? { audience: import.meta.env.VITE_OIDC_AUDIENCE }
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
