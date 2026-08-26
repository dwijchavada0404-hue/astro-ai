import { FormEvent, useEffect, useMemo, useState } from "react";
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
    const finish = async () => {
      try {
        if (window.location.pathname === "/auth/callback") {
          const signedIn = await auth.manager!.signinRedirectCallback();
          window.history.replaceState({}, "", "/");
          setUser(signedIn);
        } else {
          setUser(await auth.manager!.getUser());
        }
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "Sign-in could not be completed.");
      } finally {
        setAuthReady(true);
      }
    };
    finish();
  }, [auth]);

  if (!authReady) return <LoadingScreen />;
  const token = usableToken(user);
  if (!token) {
    return (
      <Landing
        authConfigured={auth.configured}
        backendOnline={backendOnline}
        error={error}
        onSignIn={() => auth.manager?.signinRedirect()}
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

function Workspace({ token, user, onSignOut }: { token: string; user: User; onSignOut: () => void }) {
  const [view, setView] = useState<View>("chat");
  const [profiles, setProfiles] = useState<BirthProfile[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const [profileData, conversationData] = await Promise.all([
        apiRequest<{ birth_profiles: BirthProfile[] }>("/api/v1/birth-profiles", token),
        apiRequest<{ conversations: Conversation[] }>("/api/v1/conversations", token),
      ]);
      setProfiles(profileData.birth_profiles);
      setConversations(conversationData.conversations);
    } catch (reason) {
      setError(messageFrom(reason));
    }
  };

  useEffect(() => { refresh(); }, [token]);

  const openConversation = async (id: string) => {
    setActiveId(id);
    setView("chat");
    setError("");
    try {
      const data = await apiRequest<{ messages: Message[] }>(`/api/v1/conversations/${id}`, token);
      setMessages(data.messages);
    } catch (reason) { setError(messageFrom(reason)); }
  };

  const startConversation = async () => {
    const profile = profiles.find((item) => item.is_default) || profiles[0];
    if (!profile) { setView("profiles"); return; }
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
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  const ask = async (event: FormEvent) => {
    event.preventDefault();
    const clean = question.trim();
    if (!clean || !activeId || busy) return;
    setQuestion(""); setBusy(true); setError("");
    setMessages((current) => [...current, { message_id: `local-${Date.now()}`, role: "user", content: clean }]);
    try {
      const data = await apiRequest<{ user_message: Message; assistant_message: Message }>(`/api/v1/conversations/${activeId}/ask`, token, {
        method: "POST",
        body: JSON.stringify({ question: clean, reference_moment: new Date().toISOString() }),
      });
      setMessages((current) => [...current.filter((item) => !item.message_id.startsWith("local-")), data.user_message, data.assistant_message]);
      refresh();
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  return (
    <main className="workspace">
      <aside>
        <Brand />
        <button className="new-chat" onClick={startConversation} disabled={busy}>＋ New conversation</button>
        <div className="conversation-list">
          {conversations.map((item) => <button key={item.conversation_id} className={item.conversation_id === activeId ? "active" : ""} onClick={() => openConversation(item.conversation_id)}>{item.title}</button>)}
        </div>
        <div className="aside-footer">
          <button onClick={() => setView("profiles")}>Birth profiles <span>{profiles.length}</span></button>
          <button onClick={onSignOut}>Sign out</button>
        </div>
      </aside>
      <section className="content">
        <header><div><span className="eyebrow">AstroAI workspace</span><h2>{view === "profiles" ? "Birth profiles" : "Ask your chart"}</h2></div><div className="avatar">{(user.profile.name || user.profile.email || "A").charAt(0).toUpperCase()}</div></header>
        {error && <div className="error-banner">{error}</div>}
        {view === "profiles" ? <Profiles token={token} profiles={profiles} onCreated={refresh} /> : (
          <div className="chat">
            {!activeId ? <EmptyChat hasProfile={profiles.length > 0} onStart={startConversation} onProfiles={() => setView("profiles")} /> : (
              <><div className="messages">{messages.length === 0 && <div className="prompt"><div className="star">✦</div><h3>What would you like to understand?</h3><p>Your answer will use the saved chart linked to this conversation.</p></div>}{messages.map((item) => <article key={item.message_id} className={`message ${item.role}`}><span>{item.role === "assistant" ? "✦" : "You"}</span><div>{item.content || "No narrative was returned."}{item.domain && <small>{item.domain}</small>}</div></article>)}</div><form className="composer" onSubmit={ask}><textarea aria-label="Ask AstroAI" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about career, marriage, finances, travel…" maxLength={1000} /><button disabled={busy || !question.trim()}>{busy ? "…" : "↑"}</button></form></>
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

  return <div className="profiles">
    {error && <div className="error-banner">{error}</div>}
    <div className="profile-grid">{profiles.map((profile) => <article key={profile.profile_id}>
      <span>{profile.is_default ? "Default" : "Saved"}</span>
      <h3>{profile.label}</h3>
      <p>{profile.birth_date} · {profile.birth_time}</p>
      <p>{profile.place}</p>
      {!profile.is_default && <div className="profile-actions">
        <button type="button" onClick={() => setDefault(profile)} disabled={busy}>Make default</button>
      </div>}
    </article>)}</div>
    <form className="profile-form" onSubmit={submit}><h3>Add a birth profile</h3><label>Profile name<input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} required /></label><div><label>Birth date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label><label>Exact birth time<input type="time" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} required /></label></div><label>Birth place<input value={form.place} onChange={(e) => setForm({ ...form, place: e.target.value })} placeholder="Borivali, Mumbai" required /></label><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button></form>
  </div>;
}

function EmptyChat({ hasProfile, onStart, onProfiles }: { hasProfile: boolean; onStart: () => void; onProfiles: () => void }) {
  return <div className="empty-chat"><div className="star">✦</div><h3>{hasProfile ? "Begin a new conversation" : "Create your birth profile first"}</h3><p>{hasProfile ? "AstroAI will link your default chart and preserve context across follow-up questions." : "Your birth date, exact time and place are needed to calculate a Vedic chart."}</p><button className="primary" onClick={hasProfile ? onStart : onProfiles}>{hasProfile ? "Start asking" : "Add birth profile"}</button></div>;
}

function Brand() { return <div className="brand"><span>✦</span><strong>ASTRO</strong><b>AI</b></div>; }
function messageFrom(reason: unknown) { return reason instanceof Error ? reason.message : "Something went wrong."; }
import { FormEvent, useEffect, useMemo, useState } from "react";
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
    const finish = async () => {
      try {
        if (window.location.pathname === "/auth/callback") {
          const signedIn = await auth.manager!.signinRedirectCallback();
          window.history.replaceState({}, "", "/");
          setUser(signedIn);
        } else {
          setUser(await auth.manager!.getUser());
        }
      } catch (reason) {
        setError(reason instanceof Error ? reason.message : "Sign-in could not be completed.");
      } finally {
        setAuthReady(true);
      }
    };
    finish();
  }, [auth]);

  if (!authReady) return <LoadingScreen />;
  const token = usableToken(user);
  if (!token) {
    return (
      <Landing
        authConfigured={auth.configured}
        backendOnline={backendOnline}
        error={error}
        onSignIn={() => auth.manager?.signinRedirect()}
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

function Workspace({ token, user, onSignOut }: { token: string; user: User; onSignOut: () => void }) {
  const [view, setView] = useState<View>("chat");
  const [profiles, setProfiles] = useState<BirthProfile[]>([]);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const refresh = async () => {
    try {
      const [profileData, conversationData] = await Promise.all([
        apiRequest<{ birth_profiles: BirthProfile[] }>("/api/v1/birth-profiles", token),
        apiRequest<{ conversations: Conversation[] }>("/api/v1/conversations", token),
      ]);
      setProfiles(profileData.birth_profiles);
      setConversations(conversationData.conversations);
    } catch (reason) {
      setError(messageFrom(reason));
    }
  };

  useEffect(() => { refresh(); }, [token]);

  const openConversation = async (id: string) => {
    setActiveId(id);
    setView("chat");
    setError("");
    try {
      const data = await apiRequest<{ messages: Message[] }>(`/api/v1/conversations/${id}`, token);
      setMessages(data.messages);
    } catch (reason) { setError(messageFrom(reason)); }
  };

  const startConversation = async () => {
    const profile = profiles.find((item) => item.is_default) || profiles[0];
    if (!profile) { setView("profiles"); return; }
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
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  const ask = async (event: FormEvent) => {
    event.preventDefault();
    const clean = question.trim();
    if (!clean || !activeId || busy) return;
    setQuestion(""); setBusy(true); setError("");
    setMessages((current) => [...current, { message_id: `local-${Date.now()}`, role: "user", content: clean }]);
    try {
      const data = await apiRequest<{ user_message: Message; assistant_message: Message }>(`/api/v1/conversations/${activeId}/ask`, token, {
        method: "POST",
        body: JSON.stringify({ question: clean, reference_moment: new Date().toISOString() }),
      });
      setMessages((current) => [...current.filter((item) => !item.message_id.startsWith("local-")), data.user_message, data.assistant_message]);
      refresh();
    } catch (reason) { setError(messageFrom(reason)); }
    finally { setBusy(false); }
  };

  return (
    <main className="workspace">
      <aside>
        <Brand />
        <button className="new-chat" onClick={startConversation} disabled={busy}>＋ New conversation</button>
        <div className="conversation-list">
          {conversations.map((item) => <button key={item.conversation_id} className={item.conversation_id === activeId ? "active" : ""} onClick={() => openConversation(item.conversation_id)}>{item.title}</button>)}
        </div>
        <div className="aside-footer">
          <button onClick={() => setView("profiles")}>Birth profiles <span>{profiles.length}</span></button>
          <button onClick={onSignOut}>Sign out</button>
        </div>
      </aside>
      <section className="content">
        <header><div><span className="eyebrow">AstroAI workspace</span><h2>{view === "profiles" ? "Birth profiles" : "Ask your chart"}</h2></div><div className="avatar">{(user.profile.name || user.profile.email || "A").charAt(0).toUpperCase()}</div></header>
        {error && <div className="error-banner">{error}</div>}
        {view === "profiles" ? <Profiles token={token} profiles={profiles} onCreated={refresh} /> : (
          <div className="chat">
            {!activeId ? <EmptyChat hasProfile={profiles.length > 0} onStart={startConversation} onProfiles={() => setView("profiles")} /> : (
              <><div className="messages">{messages.length === 0 && <div className="prompt"><div className="star">✦</div><h3>What would you like to understand?</h3><p>Your answer will use the saved chart linked to this conversation.</p></div>}{messages.map((item) => <article key={item.message_id} className={`message ${item.role}`}><span>{item.role === "assistant" ? "✦" : "You"}</span><div>{item.content || "No narrative was returned."}{item.domain && <small>{item.domain}</small>}</div></article>)}</div><form className="composer" onSubmit={ask}><textarea aria-label="Ask AstroAI" value={question} onChange={(event) => setQuestion(event.target.value)} placeholder="Ask about career, marriage, finances, travel…" maxLength={1000} /><button disabled={busy || !question.trim()}>{busy ? "…" : "↑"}</button></form></>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

function Profiles({ token, profiles, onCreated }: { token: string; profiles: BirthProfile[]; onCreated: () => Promise<void> }) {
  const [form, setForm] = useState({ label: "My chart", date: "", time: "", place: "" });
  const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => {
    event.preventDefault(); setBusy(true);
    try {
      await apiRequest("/api/v1/birth-profiles", token, { method: "POST", body: JSON.stringify(form) });
      setForm({ label: "My chart", date: "", time: "", place: "" });
      await onCreated();
    } finally { setBusy(false); }
  };
  return <div className="profiles"><div className="profile-grid">{profiles.map((profile) => <article key={profile.profile_id}><span>{profile.is_default ? "Default" : "Saved"}</span><h3>{profile.label}</h3><p>{profile.birth_date} · {profile.birth_time}</p><p>{profile.place}</p></article>)}</div><form className="profile-form" onSubmit={submit}><h3>Add a birth profile</h3><label>Profile name<input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} required /></label><div><label>Birth date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label><label>Exact birth time<input type="time" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} required /></label></div><label>Birth place<input value={form.place} onChange={(e) => setForm({ ...form, place: e.target.value })} placeholder="Borivali, Mumbai" required /></label><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button></form></div>;
}

function EmptyChat({ hasProfile, onStart, onProfiles }: { hasProfile: boolean; onStart: () => void; onProfiles: () => void }) {
  return <div className="empty-chat"><div className="star">✦</div><h3>{hasProfile ? "Begin a new conversation" : "Create your birth profile first"}</h3><p>{hasProfile ? "AstroAI will link your default chart and preserve context across follow-up questions." : "Your birth date, exact time and place are needed to calculate a Vedic chart."}</p><button className="primary" onClick={hasProfile ? onStart : onProfiles}>{hasProfile ? "Start asking" : "Add birth profile"}</button></div>;
}

function Brand() { return <div className="brand"><span>✦</span><strong>ASTRO</strong><b>AI</b></div>; }
function messageFrom(reason: unknown) { return reason instanceof Error ? reason.message : "Something went wrong."; }
