import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import type { User } from "oidc-client-ts";
import { apiRequest, checkHealth, type BirthProfile, type Conversation, type Message } from "./api";
import { createAuthRuntime, usableToken } from "./auth";

type View = "chat" | "profiles";

export default function App() {
  const auth = useMemo(createAuthRuntime, []);
  const [user, setUser] = useState<User | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    checkHealth().then(setBackendOnline);
    if (!auth.manager) {
      setAuthReady(true);
      return;
    }
    let active = true;
    const expireSession = () => {
      if (!active) return;
      setUser(null);
      setError("Your secure session expired. Sign in again to continue—your saved profiles and conversations are safe.");
    };
    const acceptUser = (nextUser: User) => {
      if (!active) return;
      if (nextUser.expired) expireSession();
      else { setUser(nextUser); setError(""); }
    };
    auth.manager.events.addAccessTokenExpired(expireSession);
    auth.manager.events.addUserUnloaded(expireSession);
    auth.manager.events.addUserLoaded(acceptUser);
    const finish = async () => {
      try {
        if (window.location.pathname === "/auth/callback") {
          const signedIn = await auth.manager!.signinRedirectCallback();
          window.history.replaceState({}, "", "/");
          acceptUser(signedIn);
        } else {
          const storedUser = await auth.manager!.getUser();
          if (storedUser) acceptUser(storedUser);
        }
      } catch (reason) {
        if (active) setError(reason instanceof Error ? reason.message : "Sign-in could not be completed.");
      } finally {
        if (active) setAuthReady(true);
      }
    };
    finish();
    return () => {
      active = false;
      auth.manager?.events.removeAccessTokenExpired(expireSession);
      auth.manager?.events.removeUserUnloaded(expireSession);
      auth.manager?.events.removeUserLoaded(acceptUser);
    };
  }, [auth]);

  useEffect(() => {
    const delay = tokenExpiryDelay(user?.expires_at);
    if (delay === null) return;
    if (delay === 0) {
      setUser(null);
      setError("Your secure session expired. Sign in again to continue—your saved profiles and conversations are safe.");
      return;
    }
    const timer = window.setTimeout(() => {
      setUser(null);
      setError("Your secure session expired. Sign in again to continue—your saved profiles and conversations are safe.");
    }, delay);
    return () => window.clearTimeout(timer);
  }, [user]);

  if (!authReady) return <LoadingScreen />;
  const token = usableToken(user);
  if (!token) {
    return (
      <Landing
        authConfigured={auth.configured}
        backendOnline={backendOnline}
        error={error}
        onSignIn={() => { setError(""); auth.manager?.signinRedirect(); }}
      />
    );
  }
  return <Workspace token={token} user={user!} onSignOut={() => auth.manager?.signoutRedirect()} />;
}

function LoadingScreen() {
  return <main className="loading-screen"><div className="orbit" /><p>Aligning your workspace…</p></main>;
}

function Landing({ authConfigured, backendOnline, error, onSignIn }: {
  authConfigured: boolean;
  backendOnline: boolean | null;
  error: string;
  onSignIn: () => void;
}) {
  return (
    <main className="landing">
      <nav className="nav"><Brand /><span className={`status ${backendOnline ? "online" : ""}`}>{backendOnline === null ? "Checking API" : backendOnline ? "API online" : "API unavailable"}</span></nav>
      <section className="hero">
        <div className="eyebrow">Deterministic Vedic intelligence</div>
        <h1>Your chart.<br /><span>Your questions.</span><br />Clearer direction.</h1>
        <p>Ask about career, relationships, finances, travel and more—grounded in calculated chart evidence, timing periods and your ongoing life context.</p>
        <div className="hero-actions">
          <button className="primary" disabled={!authConfigured} onClick={onSignIn}>Begin your reading <span>→</span></button>
          {!authConfigured && <small>Secure sign-in will appear when the staging identity provider is connected.</small>}
        </div>
        {error && <div className="error-banner">{error}</div>}
      </section>
      <section className="principles">
        <article><b>01</b><h3>Calculated first</h3><p>Astrological facts come from the deterministic Vedic engine—not an invented AI narrative.</p></article>
        <article><b>02</b><h3>Context that continues</h3><p>Saved profiles and conversations let follow-up questions build on what came before.</p></article>
        <article><b>03</b><h3>Evidence you can inspect</h3><p>Answers remain linked to chart factors, timing activations and conservative confidence.</p></article>
      </section>
    </main>
  );
}

export function Workspace({ token, user, onSignOut }: { token: string; user: User; onSignOut: () => void }) {
  const [view, setView] = useState<View>("chat");
  const [profiles, setProfiles] = useState<BirthProfile[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [selectedProfileId, setSelectedProfileId] = useState("");
  const [busy, setBusy] = useState(false);
  const [asking, setAsking] = useState(false);
  const [error, setError] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const refresh = async () => {
    try {
      const [profileData, conversationData] = await Promise.all([
        apiRequest<{ birth_profiles: BirthProfile[] }>("/api/v1/birth-profiles", token),
        apiRequest<{ conversations: Conversation[] }>("/api/v1/conversations", token),
      ]);
      setProfiles(profileData.birth_profiles);
      setConversations(conversationData.conversations);
      setSelectedProfileId((current) => {
        if (profileData.birth_profiles.some((profile) => profile.profile_id === current)) return current;
        return (profileData.birth_profiles.find((profile) => profile.is_default) || profileData.birth_profiles[0])?.profile_id || "";
      });
    } catch (reason) {
      setError(messageFrom(reason));
    }
  };

  useEffect(() => { refresh(); }, [token]);

  useEffect(() => {
    if (!mobileNavOpen) return;
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileNavOpen(false);
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [mobileNavOpen]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView?.({ behavior: "smooth", block: "end" });
  }, [messages, asking]);

  const openConversation = async (id: string) => {
    setActiveId(id);
    setView("chat");
    setMobileNavOpen(false);
    setError("");
    try {
      const data = await apiRequest<{ messages: Message[] }>(`/api/v1/conversations/${id}`, token);
      setMessages(data.messages);
    } catch (reason) { setError(messageFrom(reason)); }
  };

  const deleteConversation = async (conversation: Conversation) => {
    if (!window.confirm(`Delete “${conversation.title}”? This conversation and its messages will be permanently removed.`)) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/api/v1/conversations/${conversation.conversation_id}`, token, { method: "DELETE" });
      setConversations((current) => current.filter((item) => item.conversation_id !== conversation.conversation_id));
      if (activeId === conversation.conversation_id) {
        setActiveId(null);
        setMessages([]);
      }
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  const renameConversation = async (conversation: Conversation) => {
    const requested = window.prompt("Rename conversation", conversation.title);
    if (requested === null) return;
    const title = requested.trim().replace(/\s+/g, " ");
    if (!title) { setError("Conversation title cannot be empty."); return; }
    if (title.length > 120) { setError("Conversation title must be 120 characters or fewer."); return; }
    if (title === conversation.title) return;
    setBusy(true);
    setError("");
    try {
      const data = await apiRequest<{ conversation: Conversation }>(`/api/v1/conversations/${conversation.conversation_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ title }),
      });
      setConversations((current) => current.map((item) => item.conversation_id === conversation.conversation_id ? data.conversation : item));
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  const prepareConversation = () => {
    if (!profiles.length) { setView("profiles"); setMobileNavOpen(false); return; }
    setActiveId(null);
    setMessages([]);
    setView("chat");
    setMobileNavOpen(false);
  };

  const startConversation = async () => {
    const profile = profiles.find((item) => item.profile_id === selectedProfileId)
      || profiles.find((item) => item.is_default)
      || profiles[0];
    if (!profile) { setView("profiles"); setMobileNavOpen(false); return; }
    setBusy(true);
    try {
      const data = await apiRequest<{ conversation: Conversation }>("/api/v1/conversations", token, {
        method: "POST",
        body: JSON.stringify({ title: "New conversation", birth_profile_id: profile.profile_id }),
      });
      setConversations((current) => [data.conversation, ...current]);
      setActiveId(data.conversation.conversation_id);
      setMessages([]);
      setView("chat");
      setMobileNavOpen(false);
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  const ask = async (event: FormEvent) => {
    event.preventDefault();
    const clean = question.trim();
    if (!clean || !activeId || busy) return;
    const optimisticId = `local-${Date.now()}`;
    const isFirstQuestion = messages.length === 0;
    setQuestion(""); setBusy(true); setAsking(true); setError("");
    setMessages((current) => [...current, { message_id: optimisticId, role: "user", content: clean }]);
    try {
      const data = await apiRequest<{ user_message: Message; assistant_message: Message }>(`/api/v1/conversations/${activeId}/ask`, token, {
        method: "POST",
        body: JSON.stringify({ question: clean, reference_moment: new Date().toISOString() }),
      });
      setMessages((current) => [...current.filter((item) => !item.message_id.startsWith("local-")), data.user_message, data.assistant_message]);
      if (isFirstQuestion) {
        try {
          const title = conversationTitle(clean);
          const updated = await apiRequest<{ conversation: Conversation }>(`/api/v1/conversations/${activeId}`, token, {
            method: "PATCH",
            body: JSON.stringify({ title }),
          });
          setConversations((current) => current.map((item) => item.conversation_id === activeId ? updated.conversation : item));
        } catch {
          setError("Your answer was saved, but the conversation title could not be updated.");
        }
      } else {
        await refresh();
      }
    } catch (reason) {
      setMessages((current) => current.filter((item) => item.message_id !== optimisticId));
      setQuestion(clean);
      setError(messageFrom(reason));
    }
    finally { setBusy(false); setAsking(false); }
  };

  return (
    <main className="workspace">
      {mobileNavOpen && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <aside id="workspace-navigation" aria-label="Workspace navigation" className={mobileNavOpen ? "mobile-open" : ""}>
        <div className="aside-heading"><Brand /><button className="nav-close" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)}>×</button></div>
        <button className="new-chat" onClick={prepareConversation} disabled={busy}>＋ New conversation</button>
        <div className="conversation-list">
          {conversations.map((item) => <div key={item.conversation_id} className={item.conversation_id === activeId ? "conversation-row active" : "conversation-row"}>
            <button className="conversation-open" onClick={() => openConversation(item.conversation_id)}>{item.title}</button>
            <button className="conversation-rename" aria-label={`Rename ${item.title}`} title="Rename conversation" onClick={() => renameConversation(item)} disabled={busy}>✎</button>
            <button className="conversation-delete" aria-label={`Delete ${item.title}`} onClick={() => deleteConversation(item)} disabled={busy}>×</button>
          </div>)}
        </div>
        <div className="aside-footer">
          <button onClick={() => { setView("profiles"); setMobileNavOpen(false); }}>Birth profiles <span>{profiles.length}</span></button>
          <button onClick={onSignOut}>Sign out</button>
        </div>
      </aside>
      <section className="content">
        <header><div><span className="eyebrow">AstroAI workspace</span><h2>{view === "profiles" ? "Birth profiles" : "Ask your chart"}</h2></div><div className="header-actions"><button className="mobile-menu" aria-label="Open navigation" aria-controls="workspace-navigation" aria-expanded={mobileNavOpen} onClick={() => setMobileNavOpen(true)}>☰</button><div className="avatar">{(user.profile.name || user.profile.email || "A").charAt(0).toUpperCase()}</div></div></header>
        {error && <div className="error-banner">{error}</div>}
        {view === "profiles" ? <Profiles token={token} profiles={profiles} onCreated={refresh} /> : (
          <div className="chat">
            {!activeId ? <EmptyChat profiles={profiles} selectedProfileId={selectedProfileId} onSelectProfile={setSelectedProfileId} onStart={startConversation} onProfiles={() => setView("profiles")} /> : (
              <><div className="messages">{messages.length === 0 && <div className="prompt"><div className="star">✦</div><h3>What would you like to understand?</h3><p>Your answer will use the saved chart linked to this conversation.</p></div>}{messages.map((item) => <article key={item.message_id} className={`message ${item.role}`}><span>{item.role === "assistant" ? "✦" : "You"}</span><div>{item.content || "No narrative was returned."}{item.domain && <small>{item.domain}</small>}</div></article>)}{asking && <article className="message assistant thinking" role="status"><span>✦</span><div>Calculating chart factors and timing<span className="thinking-dots">…</span></div></article>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={ask}><textarea aria-label="Ask AstroAI" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (shouldSubmitQuestion(event.key, event.shiftKey)) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="Ask about career, marriage, finances, travel…" maxLength={1000} disabled={busy} /><button disabled={busy || !question.trim()}>{busy ? "…" : "↑"}</button></form></>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

export function Profiles({ token, profiles, onCreated }: { token: string; profiles: BirthProfile[]; onCreated: () => Promise<void> }) {
  const [form, setForm] = useState({ label: "My chart", date: "", time: "", place: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await apiRequest("/api/v1/birth-profiles", token, { method: "POST", body: JSON.stringify(form) });
      setForm({ label: "My chart", date: "", time: "", place: "" });
      await onCreated();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  const setDefault = async (profile: BirthProfile) => {
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/api/v1/birth-profiles/${profile.profile_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ is_default: true }),
      });
      await onCreated();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  const deleteProfile = async (profile: BirthProfile) => {
    if (!window.confirm(`Delete “${profile.label}”? This is allowed only when no conversations use this chart.`)) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/api/v1/birth-profiles/${profile.profile_id}`, token, { method: "DELETE" });
      await onCreated();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  return <div className="profiles">
    {error && <div className="error-banner">{error}</div>}
    <div className="profile-grid">{profiles.map((profile) => <article key={profile.profile_id}>
      <span>{profile.is_default ? "Default" : "Saved"}</span>
      <h3>{profile.label}</h3>
      <p>{profile.birth_date} · {profile.birth_time}</p>
      <p>{profile.place}</p>
      <div className="profile-actions">
        {!profile.is_default && <button type="button" onClick={() => setDefault(profile)} disabled={busy}>Make default</button>}
        <button type="button" className="profile-delete" onClick={() => deleteProfile(profile)} disabled={busy}>Delete</button>
      </div>
    </article>)}</div>
    <form className="profile-form" onSubmit={submit}><h3>Add a birth profile</h3><label>Profile name<input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} required /></label><div><label>Birth date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label><label>Exact birth time<input type="time" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} required /></label></div><label>Birth place<input value={form.place} onChange={(e) => setForm({ ...form, place: e.target.value })} placeholder="Borivali, Mumbai" required /></label><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button></form>
  </div>;
}

function EmptyChat({ profiles, selectedProfileId, onSelectProfile, onStart, onProfiles }: {
  profiles: BirthProfile[];
  selectedProfileId: string;
  onSelectProfile: (profileId: string) => void;
  onStart: () => void;
  onProfiles: () => void;
}) {
  const hasProfile = profiles.length > 0;
  return <div className="empty-chat"><div className="star">✦</div><h3>{hasProfile ? "Begin a new conversation" : "Create your birth profile first"}</h3><p>{hasProfile ? "Choose the chart AstroAI should use. It will remain linked to this conversation for every follow-up question." : "Your birth date, exact time and place are needed to calculate a Vedic chart."}</p>{hasProfile && <label className="chat-profile-picker">Chart for this conversation<select aria-label="Chart for this conversation" value={selectedProfileId} onChange={(event) => onSelectProfile(event.target.value)}>{profiles.map((profile) => <option key={profile.profile_id} value={profile.profile_id}>{profile.label}{profile.is_default ? " (default)" : ""}</option>)}</select></label>}<button className="primary" onClick={hasProfile ? onStart : onProfiles}>{hasProfile ? "Start asking" : "Add birth profile"}</button></div>;
}

function Brand() { return <div className="brand"><span>✦</span><strong>ASTRO</strong><b>AI</b></div>; }
function messageFrom(reason: unknown) { return reason instanceof Error ? reason.message : "Something went wrong."; }

export function conversationTitle(question: string) {
  const clean = question.trim().replace(/\s+/g, " ");
  if (clean.length <= 52) return clean;
  return `${clean.slice(0, 49).trimEnd()}…`;
}

export function shouldSubmitQuestion(key: string, shiftKey: boolean) {
  return key === "Enter" && !shiftKey;
}

export function tokenExpiryDelay(expiresAt: number | undefined, now = Date.now()) {
  if (!expiresAt) return null;
  return Math.max(0, expiresAt * 1000 - now);
}
