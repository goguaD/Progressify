import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useApp } from '../contexts/AppContext'

const TABS = ['all', 'online', 'offline']

export default function Friends() {
  const { t } = useApp()
  const navigate = useNavigate()

  const [friends, setFriends] = useState([])
  const [pending, setPending] = useState([])
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [actionMsg, setActionMsg] = useState(null) // { type: 'ok' | 'err', text }

  const [tab, setTab] = useState('all')
  const [confirmTarget, setConfirmTarget] = useState(null) // friend object or null
  const [removing, setRemoving] = useState(false)

  async function refresh() {
    try {
      const [{ data: f }, { data: p }] = await Promise.all([
        api.get('/friends'),
        api.get('/friends/requests'),
      ])
      setFriends(f)
      setPending(p)
    } catch {
      // silent
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 30_000)
    return () => clearInterval(id)
  }, [])

  // Live search (debounced)
  useEffect(() => {
    const q = search.trim()
    if (!q) { setResults([]); return }
    setSearching(true)
    const handle = setTimeout(async () => {
      try {
        const { data } = await api.get(`/users/search?q=${encodeURIComponent(q)}`)
        setResults(data)
      } catch {
        setResults([])
      } finally {
        setSearching(false)
      }
    }, 250)
    return () => clearTimeout(handle)
  }, [search])

  const onlineCount = useMemo(() => friends.filter((f) => f.is_online).length, [friends])
  const offlineCount = friends.length - onlineCount

  const visibleFriends = useMemo(() => {
    const byUsername = (a, b) => a.username.localeCompare(b.username)
    if (tab === 'online') {
      return friends.filter((f) => f.is_online).sort(byUsername)
    }
    if (tab === 'offline') {
      return friends.filter((f) => !f.is_online).sort(byUsername)
    }
    // ALL: online first, then offline; alphabetical within each group
    const online = friends.filter((f) => f.is_online).sort(byUsername)
    const offline = friends.filter((f) => !f.is_online).sort(byUsername)
    return [...online, ...offline]
  }, [friends, tab])

  async function sendRequest(username) {
    try {
      const { data } = await api.post('/friends/request', { username })
      setActionMsg({
        type: 'ok',
        text: data?.auto_accepted ? t.friends_request_friends : t.friends_request_sent,
      })
      setSearch('')
      setResults([])
      refresh()
    } catch (err) {
      setActionMsg({ type: 'err', text: err.response?.data?.detail || 'Error' })
    }
  }

  async function accept(id) {
    await api.post(`/friends/accept/${id}`).catch(() => {})
    refresh()
  }

  async function decline(id) {
    await api.post(`/friends/decline/${id}`).catch(() => {})
    refresh()
  }

  async function confirmRemove() {
    if (!confirmTarget) return
    setRemoving(true)
    try {
      await api.delete(`/friends/${confirmTarget.id}`)
    } catch {
      // ignore
    } finally {
      setRemoving(false)
      setConfirmTarget(null)
      refresh()
    }
  }

  const tabCounts = {
    all: friends.length,
    online: onlineCount,
    offline: offlineCount,
  }

  return (
    <div className="friends-page">
      <div className="friends-grid">
        {/* ── Main column ──────────────────────────────────────── */}
        <div className="friends-main">
          <div className="friends-header">
            <h1 className="friends-title">{t.friends_title} 👥</h1>
            <p className="friends-subtitle">{t.friends_sub}</p>
          </div>

          {/* Filter tabs */}
          <div className="filter-tabs" role="tablist">
            {TABS.map((id) => (
              <button
                key={id}
                role="tab"
                aria-selected={tab === id}
                className={`filter-tab ${tab === id ? 'active' : ''}`}
                onClick={() => setTab(id)}
              >
                {t[`friends_tab_${id}`]}
                <span className="filter-tab-count">{tabCounts[id]}</span>
              </button>
            ))}
          </div>

          {loading && <p className="muted">{t.admin_loading}</p>}

          {!loading && friends.length === 0 && (
            <div className="empty-card">{t.friends_no_friends}</div>
          )}

          {!loading && friends.length > 0 && visibleFriends.length === 0 && (
            <div className="empty-card">
              {tab === 'online' ? t.friends_no_online : t.friends_no_offline}
            </div>
          )}

          {visibleFriends.length > 0 && (
            <div className="friends-list">
              {visibleFriends.map((f) => (
                <FriendCard
                  key={f.id}
                  friend={f}
                  t={t}
                  onClick={() => navigate(`/u/${f.username}`)}
                  onRemoveClick={() => setConfirmTarget(f)}
                />
              ))}
            </div>
          )}
        </div>

        {/* ── Side column ──────────────────────────────────────── */}
        <aside className="friends-side">
          {/* Stats */}
          <div className="side-card">
            <div className="stat-grid">
              <Stat label={t.friends_total} value={friends.length} />
              <Stat label={t.friends_online} value={onlineCount} accent />
              <Stat label={t.friends_offline} value={offlineCount} />
              <Stat label={t.friends_pending} value={pending.length} warn={pending.length > 0} />
            </div>
          </div>

          {/* Add friend */}
          <div className="side-card">
            <p className="side-card-title">{t.friends_add}</p>
            <div className="search-box">
              <input
                value={search}
                onChange={(e) => { setSearch(e.target.value); setActionMsg(null) }}
                placeholder={t.friends_add_ph}
                style={{ marginBottom: 0 }}
              />
            </div>

            {actionMsg && (
              <p className={`tiny-msg ${actionMsg.type === 'ok' ? 'ok' : 'err'}`}>
                {actionMsg.text}
              </p>
            )}

            {search && (
              <div className="search-results">
                {searching && <p className="muted">…</p>}
                {!searching && results.length === 0 && (
                  <p className="muted">{t.friends_search_empty}</p>
                )}
                {results.map((u) => (
                  <div key={u.id} className="search-row">
                    <button
                      type="button"
                      className="search-row-info"
                      onClick={() => navigate(`/u/${u.username}`)}
                    >
                      <Avatar user={u} small />
                      <div>
                        <div className="search-row-name">@{u.username}</div>
                        <div className="search-row-sub">
                          {u.firstname} {u.lastname}
                        </div>
                      </div>
                    </button>
                    <button
                      className="btn btn-primary btn-tiny"
                      onClick={() => sendRequest(u.username)}
                    >
                      {t.friends_add_btn}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Pending requests */}
          <div className="side-card">
            <p className="side-card-title">
              {t.friends_pending_section} {pending.length > 0 && <span className="pill">{pending.length}</span>}
            </p>
            {pending.length === 0 && <p className="muted">{t.friends_no_pending}</p>}
            {pending.map((req) => (
              <div key={req.id} className="pending-row">
                <button
                  type="button"
                  className="pending-info"
                  onClick={() => navigate(`/u/${req.requester.username}`)}
                >
                  <Avatar user={req.requester} small />
                  <div>
                    <div className="search-row-name">@{req.requester.username}</div>
                    <div className="search-row-sub">
                      {req.requester.firstname} {req.requester.lastname}
                    </div>
                  </div>
                </button>
                <div className="pending-actions">
                  <button className="btn btn-primary btn-tiny" onClick={() => accept(req.id)}>
                    {t.friends_accept}
                  </button>
                  <button className="btn btn-secondary btn-tiny" onClick={() => decline(req.id)}>
                    {t.friends_decline}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </aside>
      </div>

      {confirmTarget && (
        <ConfirmModal
          t={t}
          target={confirmTarget}
          busy={removing}
          onCancel={() => !removing && setConfirmTarget(null)}
          onConfirm={confirmRemove}
        />
      )}
    </div>
  )
}

// ─── helpers ─────────────────────────────────────────────────────────────────

function Stat({ label, value, accent, warn }) {
  return (
    <div className={`stat ${accent ? 'stat-accent' : ''} ${warn ? 'stat-warn' : ''}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

function Avatar({ user, small }) {
  const initials = ((user.firstname?.[0] || '') + (user.lastname?.[0] || '')).toUpperCase() || '?'
  return (
    <div className={`avatar ${small ? 'avatar-sm' : ''} ${user.is_online ? 'is-online' : ''}`}>
      <span>{initials}</span>
      {typeof user.is_online === 'boolean' && (
        <span className={`status-dot ${user.is_online ? 'online' : 'offline'}`} />
      )}
    </div>
  )
}

function FriendCard({ friend, t, onClick, onRemoveClick }) {
  const goalLabel = friend.goal ? (t.goals[friend.goal] || friend.goal) : '—'

  return (
    <div className="friend-card">
      <button type="button" className="friend-card-main" onClick={onClick}>
        <Avatar user={friend} />
        <div className="friend-card-text">
          <div className="friend-card-top">
            <span className="friend-card-name">{friend.firstname} {friend.lastname}</span>
            <span className={`friend-status ${friend.is_online ? 'online' : 'offline'}`}>
              {friend.is_online ? t.friends_status_online : t.friends_status_offline}
            </span>
          </div>
          <div className="friend-card-handle">@{friend.username} · {goalLabel}</div>
          <div className="friend-card-meta">
            <span><b>{t.friends_workout}:</b> {friend.current_workout || '—'}</span>
            <span><b>{t.friends_meal}:</b> {friend.current_meal_plan || '—'}</span>
          </div>
          {friend.last_activity && (
            <div className="friend-card-activity">{friend.last_activity}</div>
          )}
        </div>
      </button>

      <button
        type="button"
        className="btn btn-danger btn-tiny friend-remove-btn"
        onClick={(e) => { e.stopPropagation(); onRemoveClick() }}
      >
        {t.friends_remove_btn}
      </button>
    </div>
  )
}

function ConfirmModal({ t, target, busy, onCancel, onConfirm }) {
  // Close on ESC
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape' && !busy) onCancel() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [busy, onCancel])

  const text = t.confirm_unfriend_text.replace('{username}', target.username)

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <h3 className="modal-title">{t.confirm_unfriend_title}</h3>
        <p className="modal-text">{text}</p>
        <div className="modal-actions">
          <button className="btn btn-secondary" disabled={busy} onClick={onCancel}>
            {t.confirm_no}
          </button>
          <button className="btn btn-danger" disabled={busy} onClick={onConfirm} autoFocus>
            {busy ? '…' : t.confirm_yes}
          </button>
        </div>
      </div>
    </div>
  )
}
