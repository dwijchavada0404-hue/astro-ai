import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import type { User } from "oidc-client-ts";
import { apiDownload, apiRequest, checkHealth, type BirthProfile, type Conversation, type Message } from "./api";
import { createAuthRuntime, usableToken } from "./auth";
import { parseAstroAiBackup } from "./backup";

type View = "chat" | "profiles";
export type LegalPageId = "privacy" | "terms" | "disclaimer";

export function evidenceLabels(payload: unknown): string[] {
  const value = payload && typeof payload === "object" ? payload as Record<string, unknown> : {};
  const result = value.result && typeof value.result === "object" ? value.result as Record<string, unknown> : value;
  const evidence = Array.isArray(result.evidence) ? result.evidence : Array.isArray(result.indicators) ? result.indicators : [];
  return evidence.map((item) => {
    if (typeof item === "string") return item;
    if (!item || typeof item !== "object") return null;
    const detail = item as Record<string, unknown>;
    return [detail.interpretation, detail.summary, detail.factor, detail.rule, detail.theme].find((entry) => typeof entry === "string" && entry.trim()) as string | undefined;
  }).filter((item): item is string => Boolean(item)).slice(0, 5);
}

export function filterConversations(conversations: Conversation[], query: string): Conversation[] {
  const clean = query.trim().replace(/\s+/g, " ").toLocaleLowerCase();
  if (!clean) return conversations;
  return conversations.filter((conversation) => conversation.title.toLocaleLowerCase().includes(clean));
}

export const STARTER_QUESTIONS = [
  "What does my chart suggest about my career direction over the next year?",
  "What relationship patterns are most important for me to understand?",
  "What does my chart suggest about my financial growth and stability?",
  "Is this a supportive period for travel or relocation?",
] as const;

export default function App() {
  const legalPage = legalPageFromPath(window.location.pathname);
  if (legalPage) return <LegalDocument page={legalPage} />;
  return <AuthenticatedApp />;
}

function AuthenticatedApp() {
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
          {authConfigured && <small className="legal-consent">By continuing, you agree to the <a href="/terms">Terms</a> and acknowledge the <a href="/privacy">Privacy Notice</a> and <a href="/disclaimer">Safety Disclaimer</a>.</small>}
        </div>
        {error && <div className="error-banner">{error}</div>}
      </section>
      <section className="principles">
        <article><b>01</b><h3>Calculated first</h3><p>Astrological facts come from the deterministic Vedic engine—not an invented AI narrative.</p></article>
        <article><b>02</b><h3>Context that continues</h3><p>Saved profiles and conversations let follow-up questions build on what came before.</p></article>
        <article><b>03</b><h3>Evidence you can inspect</h3><p>Answers remain linked to chart factors, timing activations and conservative confidence.</p></article>
      </section>
      <LegalFooter />
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
  const [conversationSearch, setConversationSearch] = useState("");
  const [busy, setBusy] = useState(false);
  const [asking, setAsking] = useState(false);
  const [copiedMessageId, setCopiedMessageId] = useState<string | null>(null);
  const [evidenceOpenId, setEvidenceOpenId] = useState<string | null>(null);
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
      const data = await apiRequest<{ conversation: Conversation; messages: Message[] }>(`/api/v1/conversations/${id}`, token);
      setMessages(data.messages);
      setConversations((current) => current.map((item) => item.conversation_id === id ? data.conversation : item));
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

  const copyAnswer = async (message: Message) => {
    if (!message.content) return;
    setError("");
    try {
      if (!navigator.clipboard?.writeText) throw new Error("Clipboard access is unavailable in this browser.");
      await navigator.clipboard.writeText(message.content);
      setCopiedMessageId(message.message_id);
    } catch (reason) {
      setError(messageFrom(reason));
    }
  };

  const chooseStarterQuestion = (starter: string) => { setQuestion(starter); setError(""); };

  const activeConversation = conversations.find((item) => item.conversation_id === activeId);
  const activeProfile = profiles.find((item) => item.profile_id === activeConversation?.birth_profile_id);
  const visibleConversations = useMemo(() => filterConversations(conversations, conversationSearch), [conversations, conversationSearch]);

  return (
    <main className="workspace">
      {mobileNavOpen && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <aside id="workspace-navigation" aria-label="Workspace navigation" className={mobileNavOpen ? "mobile-open" : ""}>
        <div className="aside-heading"><Brand /><button className="nav-close" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)}>×</button></div>
        <button className="new-chat" onClick={prepareConversation} disabled={busy}>＋ New conversation</button>
        <input className="new-chat" type="search" aria-label="Search conversations" placeholder="Search conversations…" value={conversationSearch} onChange={(event) => setConversationSearch(event.target.value)} />
        <div className="conversation-list">
          {visibleConversations.map((item) => <div key={item.conversation_id} className={item.conversation_id === activeId ? "conversation-row active" : "conversation-row"}>
            <button className="conversation-open" onClick={() => openConversation(item.conversation_id)}>{item.title}</button>
            <button className="conversation-rename" aria-label={`Rename ${item.title}`} title="Rename conversation" onClick={() => renameConversation(item)} disabled={busy}>✎</button>
            <button className="conversation-delete" aria-label={`Delete ${item.title}`} onClick={() => deleteConversation(item)} disabled={busy}>×</button>
          </div>)}
          {conversationSearch.trim() && visibleConversations.length === 0 && <div className="status">No matching conversations</div>}
        </div>
        <div className="aside-footer">
          <button onClick={() => { setView("profiles"); setMobileNavOpen(false); }}>Birth profiles <span>{profiles.length}</span></button>
          <button onClick={onSignOut}>Sign out</button>
          <LegalLinks />
        </div>
      </aside>
      <section className="content">
        <header><div><span className="eyebrow">AstroAI workspace</span><h2>{view === "profiles" ? "Birth profiles" : "Ask your chart"}</h2>{view === "chat" && activeConversation && <span className={`active-chart ${activeProfile ? "" : "missing"}`} aria-label="Active birth profile">✦ {activeProfile?.label || "Linked chart unavailable"}</span>}</div><div className="header-actions"><button className="mobile-menu" aria-label="Open navigation" aria-controls="workspace-navigation" aria-expanded={mobileNavOpen} onClick={() => setMobileNavOpen(true)}>☰</button><div className="avatar">{(user.profile.name || user.profile.email || "A").charAt(0).toUpperCase()}</div></div></header>
        {error && <div className="error-banner">{error}</div>}
        {view === "profiles" ? <Profiles token={token} profiles={profiles} onCreated={refresh} onDataDeleted={onSignOut} /> : (
          <div className="chat">
            {!activeId ? <EmptyChat profiles={profiles} selectedProfileId={selectedProfileId} onSelectProfile={setSelectedProfileId} onStart={startConversation} onProfiles={() => setView("profiles")} /> : (
              <><div className="messages">{messages.length === 0 && <div className="prompt"><div className="star">✦</div><h3>What would you like to understand?</h3><p>Your answer will use the saved chart linked to this conversation.</p><div className="starter-questions" aria-label="Question starters">{STARTER_QUESTIONS.map((starter) => <button key={starter} type="button" onClick={() => chooseStarterQuestion(starter)} disabled={busy || asking}>{starter}</button>)}</div></div>}{messages.map((item) => <article key={item.message_id} className={`message ${item.role}`}><span>{item.role === "assistant" ? "✦" : "You"}</span><div>{item.content || "No narrative was returned."}{item.domain && <small>{item.domain}</small>}{item.role === "assistant" && item.content && <><button className="answer-copy" type="button" aria-label="Copy answer" onClick={() => copyAnswer(item)}>{copiedMessageId === item.message_id ? "Copied" : "Copy"}</button>{evidenceLabels(item.payload).length > 0 && <><button className="answer-evidence" type="button" aria-expanded={evidenceOpenId === item.message_id} onClick={() => setEvidenceOpenId((current) => current === item.message_id ? null : item.message_id)}>{evidenceOpenId === item.message_id ? "Hide supporting factors" : "Why this answer?"}</button>{evidenceOpenId === item.message_id && <ul className="evidence-list">{evidenceLabels(item.payload).map((label) => <li key={label}>{label}</li>)}</>}</>}</>}</div></article>)}{asking && <article className="message assistant thinking" role="status"><span>✦</span><div>Calculating chart factors and timing<span className="thinking-dots">…</span></div></article>}<div ref={messagesEndRef} /></div><form className="composer" onSubmit={ask}><textarea aria-label="Ask AstroAI" value={question} onChange={(event) => setQuestion(event.target.value)} onKeyDown={(event) => { if (shouldSubmitQuestion(event.key, event.shiftKey)) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} placeholder="Ask about career, marriage, finances, travel…" maxLength={1000} disabled={busy} /><button disabled={busy || !question.trim()}>{busy ? "…" : "↑"}</button></form><p className="composer-disclaimer">Astrology is for reflection and entertainment—not medical, legal, financial or other professional advice.</p></>
            )}
          </div>
        )}
      </section>
    </main>
  );
}

export function Profiles({ token, profiles, onCreated, onDataDeleted }: { token: string; profiles: BirthProfile[]; onCreated: () => Promise<void>; onDataDeleted?: () => void }) {
  const [form, setForm] = useState({ label: "My chart", date: "", time: "", place: "" });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [restoreNotice, setRestoreNotice] = useState("");

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

  const renameProfile = async (profile: BirthProfile) => {
    const requested = window.prompt("Rename birth profile", profile.label);
    if (requested === null) return;
    const label = requested.trim().replace(/\s+/g, " ");
    if (!label) { setError("Profile name cannot be empty."); return; }
    if (label.length > 80) { setError("Profile name must be 80 characters or fewer."); return; }
    if (label === profile.label) return;
    setBusy(true);
    setError("");
    try {
      await apiRequest(`/api/v1/birth-profiles/${profile.profile_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ label }),
      });
      await onCreated();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  const duplicateAndCorrectProfile = async (profile: BirthProfile) => {
    const requestedLabel = window.prompt("Name the corrected birth profile", `${profile.label} (corrected)`);
    if (requestedLabel === null) return;
    const label = requestedLabel.trim().replace(/\s+/g, " ");
    if (!label) { setError("Profile name cannot be empty."); return; }
    if (label.length > 80) { setError("Profile name must be 80 characters or fewer."); return; }
    const date = window.prompt("Correct birth date (YYYY-MM-DD)", profile.birth_date);
    if (date === null) return;
    const time = window.prompt("Correct exact birth time (HH:MM)", profile.birth_time.slice(0, 5));
    if (time === null) return;
    const place = window.prompt("Correct birth place", profile.place);
    if (place === null) return;
    if (!date.trim() || !time.trim() || !place.trim()) { setError("Birth date, exact time and place are required."); return; }

    setBusy(true);
    setError("");
    try {
      const duplicated = await apiRequest<{ birth_profile: BirthProfile }>(`/api/v1/birth-profiles/${profile.profile_id}/duplicate`, token, {
        method: "POST",
        body: JSON.stringify({ label }),
      });
      await apiRequest(`/api/v1/birth-profiles/${duplicated.birth_profile.profile_id}`, token, {
        method: "PATCH",
        body: JSON.stringify({ date: date.trim(), time: time.trim(), place: place.trim() }),
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

  const deleteAllData = async () => {
    const confirmation = window.prompt("This permanently deletes every AstroAI profile, conversation and message. Type DELETE to continue.");
    if (confirmation !== "DELETE") return;
    setBusy(true);
    setError("");
    try {
      await apiRequest("/api/v1/profile", token, { method: "DELETE" });
      onDataDeleted?.();
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  const exportData = async () => {
    setBusy(true);
    setError("");
    try {
      const blob = await apiDownload("/api/v1/profile/export", token);
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "astroai-data-export.json";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
    }
  };

  const importData = async (event: FormEvent<HTMLInputElement>) => {
    const input = event.currentTarget;
    const file = input.files?.[0];
    if (!file) return;
    setError("");
    setRestoreNotice("");
    try {
      const backup = parseAstroAiBackup(await file.text());
      const profileCount = Array.isArray(backup.birth_profiles) ? backup.birth_profiles.length : 0;
      const conversationCount = Array.isArray(backup.conversations) ? backup.conversations.length : 0;
      if (!window.confirm(`Restore ${profileCount} birth profile${profileCount === 1 ? "" : "s"} and ${conversationCount} conversation${conversationCount === 1 ? "" : "s"} from this backup? Existing AstroAI data will be kept.`)) return;
      setBusy(true);
      const data = await apiRequest<{ imported: { birth_profiles: number; conversations: number; messages: number; unlinked_conversations: number } }>("/api/v1/profile/import", token, {
        method: "POST",
        body: JSON.stringify(backup),
      });
      await onCreated();
      const imported = data.imported;
      setRestoreNotice(`Restored ${imported.birth_profiles} birth profile${imported.birth_profiles === 1 ? "" : "s"}, ${imported.conversations} conversation${imported.conversations === 1 ? "" : "s"}, and ${imported.messages} message${imported.messages === 1 ? "" : "s"}.${imported.unlinked_conversations ? ` ${imported.unlinked_conversations} conversation${imported.unlinked_conversations === 1 ? "" : "s"} could not be linked to a restored birth profile.` : ""}`);
    } catch (reason) {
      setError(messageFrom(reason));
    } finally {
      setBusy(false);
      input.value = "";
    }
  };

  return <div className="profiles">
    {error && <div className="error-banner">{error}</div>}
    {restoreNotice && <div className="restore-notice" role="status">{restoreNotice}</div>}
    <div className="profile-grid">{profiles.map((profile) => <article key={profile.profile_id}>
      <span>{profile.is_default ? "Default" : "Saved"}</span>
      <h3>{profile.label}</h3>
      <p>{profile.birth_date} · {profile.birth_time}</p>
      <p>{profile.place}</p>
      <div className="profile-actions">
        {!profile.is_default && <button type="button" onClick={() => setDefault(profile)} disabled={busy}>Make default</button>}
        <button type="button" onClick={() => renameProfile(profile)} disabled={busy}>Rename</button>
        <button type="button" onClick={() => duplicateAndCorrectProfile(profile)} disabled={busy}>Duplicate &amp; correct</button>
        <button type="button" className="profile-delete" onClick={() => deleteProfile(profile)} disabled={busy}>Delete</button>
      </div>
    </article>)}</div>
    <form className="profile-form" onSubmit={submit}><h3>Add a birth profile</h3><label>Profile name<input value={form.label} onChange={(e) => setForm({ ...form, label: e.target.value })} required /></label><div><label>Birth date<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label><label>Exact birth time<input type="time" value={form.time} onChange={(e) => setForm({ ...form, time: e.target.value })} required /></label></div><label>Birth place<input value={form.place} onChange={(e) => setForm({ ...form, place: e.target.value })} placeholder="Borivali, Mumbai" required /></label><button className="primary" disabled={busy}>{busy ? "Saving…" : "Save profile"}</button></form>
    {onDataDeleted && <section className="danger-zone"><h3>Your AstroAI data</h3><p>Download a portable copy of your saved charts and conversations, restore a previous AstroAI export without overwriting current data, or permanently delete your application data. Your identity-provider login is managed separately.</p><div className="data-actions"><button type="button" onClick={exportData} disabled={busy}>Export my data</button><label className={busy ? "restore-upload disabled" : "restore-upload"}>Restore backup<input type="file" accept="application/json,.json" onInput={importData} disabled={busy} /></label><button type="button" onClick={deleteAllData} disabled={busy}>Delete all AstroAI data</button></div></section>}
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

const LEGAL_CONTENT: Record<LegalPageId, { title: string; intro: string; sections: { heading: string; body: string }[] }> = {
  privacy: {
    title: "Privacy Notice",
    intro: "This notice explains what AstroAI collects, why it is used, where it is processed, and the choices available to you.",
    sections: [
      { heading: "Information we process", body: "We process your identity-provider account identifier and available profile claims, birth-profile details you enter (including date, exact time and place), questions, conversations, and basic technical/security logs needed to operate the service." },
      { heading: "How we use it", body: "We use this information to authenticate you, calculate charts, answer questions, preserve your profiles and conversation history, secure the service, diagnose faults, and prevent abuse. We do not sell your personal information or use your birth data for advertising." },
      { heading: "Storage and service providers", body: "Application data is hosted on Railway in the EU region. Authentication is provided by Auth0 in the EU region. These providers process information on AstroAI’s behalf under their respective security and privacy terms. Internet access may involve processing across countries." },
      { heading: "Retention and deletion", body: "Your application data is retained while your AstroAI account is active. You can permanently delete saved charts, conversations, messages and AstroAI account metadata from Birth profiles → Delete all AstroAI data. Your Auth0 identity is managed separately and may require a separate provider-side request." },
      { heading: "Your choices and rights", body: "You can review and manage saved profiles and conversations in the app, delete individual eligible records, or delete all AstroAI application data. Depending on applicable law, you may also request access, correction, restriction, portability or objection." },
      { heading: "Security and children", body: "We use encrypted HTTPS transport, authenticated API access, restricted hosts, request limits and persistent storage controls. No online service is risk-free. AstroAI is intended for adults aged 18 or older and is not directed to children." },
      { heading: "Questions", body: "For a privacy or data-rights request during staging, contact the project owner through the AstroAI GitHub repository issue channel. We may update this notice as the service changes." },
    ],
  },
  terms: {
    title: "Terms of Use",
    intro: "By accessing AstroAI, you agree to these terms. Do not use the service if you do not agree.",
    sections: [
      { heading: "Eligibility and account", body: "You must be at least 18 years old and provide accurate information. You are responsible for activity performed through your identity-provider account and for keeping that account secure." },
      { heading: "Permitted use", body: "AstroAI may be used for lawful personal reflection and entertainment. You must not probe or disrupt the service, bypass access controls or rate limits, automate abusive traffic, misuse another person’s data, or use outputs to harm, discriminate against or deceive anyone." },
      { heading: "Astrology outputs", body: "Outputs are symbolic interpretations generated from deterministic chart calculations and rule-based synthesis. They are not facts, guarantees or predictions of certain outcomes and must not replace your own judgment or qualified professional advice." },
      { heading: "Availability and changes", body: "This is a staging service. Features may change, be corrected, suspended or withdrawn, and stored data may be unavailable during maintenance or technical failure. We may update these terms and will publish the revised date." },
      { heading: "No warranty and limited responsibility", body: "The service is provided on an “as is” and “as available” basis to the extent permitted by law. AstroAI does not warrant accuracy, fitness for a particular purpose or uninterrupted availability, and is not responsible for decisions made in reliance on an output." },
      { heading: "Suspension", body: "Access may be limited or terminated where necessary to protect users or infrastructure, respond to legal requirements, investigate misuse, or enforce these terms." },
      { heading: "Free software licence", body: "AstroAI is free software provided under the GNU Affero General Public License version 3. The complete corresponding source code is available through the Source link on this page. You may use, study, modify and redistribute the software subject to that licence." },
    ],
  },
  disclaimer: {
    title: "Astrology & Safety Disclaimer",
    intro: "AstroAI is a reflective astrology tool. Its outputs are not professional advice and should never be treated as certain predictions.",
    sections: [
      { heading: "No medical advice", body: "Do not use AstroAI to diagnose symptoms, choose or stop treatment, assess emergencies, pregnancy, fertility, mental health risk, or life expectancy. Consult a qualified healthcare professional. In an emergency, contact local emergency services." },
      { heading: "No financial or legal advice", body: "Do not use an astrology response as the basis for investments, borrowing, insurance, tax, contracts, litigation or other material financial or legal decisions. Consult an appropriately qualified professional." },
      { heading: "No guaranteed outcomes", body: "Astrological timings and interpretations are symbolic and uncertain. AstroAI cannot guarantee marriage, employment, wealth, health, travel, legal outcomes, another person’s behavior, or any specific future event." },
      { heading: "Your responsibility", body: "Use outputs as one optional perspective, verify important information independently, consider real-world evidence and circumstances, and make your own decisions. Avoid entering unnecessary sensitive information in questions." },
    ],
  },
};

export function legalPageFromPath(pathname: string): LegalPageId | null {
  const page = pathname.replace(/^\/+|\/+$/g, "");
  return page === "privacy" || page === "terms" || page === "disclaimer" ? page : null;
}

export function LegalDocument({ page }: { page: LegalPageId }) {
  const document = LEGAL_CONTENT[page];
  return <main className="legal-page"><nav className="nav"><a href="/" aria-label="AstroAI home"><Brand /></a><a href="/">Back to AstroAI</a></nav><article><span className="eyebrow">Last updated 30 August 2026</span><h1>{document.title}</h1><p className="legal-intro">{document.intro}</p>{document.sections.map((section) => <section key={section.heading}><h2>{section.heading}</h2><p>{section.body}</p></section>)}</article><LegalFooter /></main>;
}

function LegalLinks() { return <div className="legal-links"><a href="/privacy">Privacy</a><a href="/terms">Terms</a><a href="/disclaimer">Disclaimer</a><a href="https://github.com/dwijchavada0404-hue/astro-ai">Source (AGPL-3.0)</a></div>; }
function LegalFooter() { return <footer className="legal-footer"><LegalLinks /><p>© 2026 AstroAI · <a href="https://github.com/dwijchavada0404-hue/astro-ai/issues">Contact</a> · For reflection and entertainment only.</p></footer>; }
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