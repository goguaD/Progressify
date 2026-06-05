import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import ConfirmUnfriendModal from '../components/friends/ConfirmUnfriendModal'
import FriendCard from '../components/friends/FriendCard'
import FriendSearch from '../components/friends/FriendSearch'
import PendingRequests from '../components/friends/PendingRequests'
import { useApp } from '../contexts/AppContext'

const TABS = ['all', 'online', 'offline']

function Stat({ label, value, accent, warn }) {
  return (
    <div className={`stat ${accent ? 'stat-accent' : ''} ${warn ? 'stat-warn' : ''}`}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  )
}

export default function Friends() {
  const { t } = useApp()
  const navigate = useNavigate()

  const [friends, setFriends] = useState([])
  const [pending, setPending] = useState([])
  const [loading, setLoading] = useState(true)

  const [search, setSearch] = useState('')
  const [results, setResults] = useState([])
  const [searching, setSearching] = useState(false)
  const [actionMsg, setActionMsg] = useState(null)

  const [tab, setTab] = useState('all')
  const [confirmTarget, setConfirmTarget] = useState(null)
  const [removing, setRemoving] = useState(false)
  const [h2hMap, setH2hMap] = useState({})

  async function refresh() {
    try {
      const [{ data: f }, { data: p }] = await Promise.all([
        api.get('/friends'),
        api.get('/friends/requests'),
      ])
      setFriends(f)
      setPending(p)
    } catch {
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
    const id = setInterval(refresh, 30_000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    if (friends.length === 0) return
    Promise.all(
      friends.map((f) =>
        api.get(`/challenges/h2h/${f.id}`).then(({ data }) => [f.id, data]).catch(() => null)
      )
    ).then((results) => {
      const map = {}
      for (const r of results) {
        if (r) map[r[0]] = r[1]
      }
      setH2hMap(map)
    })
  }, [friends])

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
    if (tab === 'online') return friends.filter((f) => f.is_online).sort(byUsername)
    if (tab === 'offline') return friends.filter((f) => !f.is_online).sort(byUsername)
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
    try { await api.delete(`/friends/${confirmTarget.id}`) } catch {}
    setRemoving(false)
    setConfirmTarget(null)
    refresh()
  }

  const tabCounts = { all: friends.length, online: onlineCount, offline: offlineCount }

  return (
    <div className="friends-page">
      <div className="friends-grid">
        <div className="friends-main">
          <div className="friends-header">
            <h1 className="friends-title">{t.friends_title} 👥</h1>
            <p className="friends-subtitle">{t.friends_sub}</p>
          </div>

          <div className="filter-tabs" role="tablist">
            {TABS.map((id) => (
              <button key={id} role="tab" aria-selected={tab === id}
                className={`filter-tab ${tab === id ? 'active' : ''}`}
                onClick={() => setTab(id)}>
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
                  onChallenge={() => navigate('/challenges')}
                  h2h={h2hMap[f.id]}
                />
              ))}
            </div>
          )}
        </div>

        <aside className="friends-side">
          <div className="side-card">
            <div className="stat-grid">
              <Stat label={t.friends_total} value={friends.length} />
              <Stat label={t.friends_online} value={onlineCount} accent />
              <Stat label={t.friends_offline} value={offlineCount} />
              <Stat label={t.friends_pending} value={pending.length} warn={pending.length > 0} />
            </div>
          </div>

          <FriendSearch
            search={search} setSearch={setSearch}
            results={results} searching={searching}
            actionMsg={actionMsg} setActionMsg={setActionMsg}
            sendRequest={sendRequest} t={t}
          />

          <PendingRequests pending={pending} accept={accept} decline={decline} t={t} />
        </aside>
      </div>

      {confirmTarget && (
        <ConfirmUnfriendModal
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
