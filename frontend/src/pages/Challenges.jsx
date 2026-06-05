import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import ChallengeCard from '../components/challenges/ChallengeCard'
import CreateChallengeModal from '../components/challenges/CreateChallengeModal'
import DeadlinePopup from '../components/challenges/DeadlinePopup'
import { useApp } from '../contexts/AppContext'

const TABS = ['all', 'pending', 'active', 'completed']

export default function Challenges() {
  const { t } = useApp()
  const navigate = useNavigate()

  const [challenges, setChallenges] = useState([])
  const [loading, setLoading] = useState(true)
  const [tab, setTab] = useState('all')
  const [showCreate, setShowCreate] = useState(false)
  const [friends, setFriends] = useState([])
  const [deadlineAlert, setDeadlineAlert] = useState(null)

  async function refresh() {
    try {
      const { data } = await api.get('/challenges')
      setChallenges(data)
      const urgent = data.find((c) => c.deadline_soon && c.status === 'accepted')
      if (urgent) setDeadlineAlert(urgent)
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

  async function openCreate() {
    try { const { data } = await api.get('/friends'); setFriends(data) } catch {}
    setShowCreate(true)
  }

  const visible = useMemo(() => {
    if (tab === 'all') return challenges
    if (tab === 'pending') return challenges.filter((c) => c.status === 'pending')
    if (tab === 'active') return challenges.filter((c) => c.status === 'accepted')
    return challenges.filter((c) => ['completed', 'declined', 'expired'].includes(c.status))
  }, [challenges, tab])

  const tabCounts = {
    all: challenges.length,
    pending: challenges.filter((c) => c.status === 'pending').length,
    active: challenges.filter((c) => c.status === 'accepted').length,
    completed: challenges.filter((c) => ['completed', 'declined', 'expired'].includes(c.status)).length,
  }

  return (
    <div className="challenges-page">
      <DeadlinePopup alert={deadlineAlert} t={t} onClose={() => setDeadlineAlert(null)} />

      <div className="challenges-header">
        <h1 className="challenges-title">{t.ch_challenge} ⚔️</h1>
        <button className="btn btn-primary" style={{ width: 'auto', padding: '10px 20px' }}
          onClick={openCreate}>
          + {t.ch_send_title}
        </button>
      </div>

      <div className="filter-tabs" role="tablist">
        {TABS.map((id) => (
          <button key={id} role="tab" aria-selected={tab === id}
            className={`filter-tab ${tab === id ? 'active' : ''}`}
            onClick={() => setTab(id)}>
            {t[`ch_tab_${id}`]}
            <span className="filter-tab-count">{tabCounts[id]}</span>
          </button>
        ))}
      </div>

      {loading && <p className="muted">…</p>}
      {!loading && visible.length === 0 && <div className="empty-card">{t.ch_no_challenges}</div>}

      <div className="challenges-list">
        {visible.map((ch) => (
          <ChallengeCard key={ch.id} ch={ch} t={t} navigate={navigate} onRefresh={refresh} />
        ))}
      </div>

      {showCreate && (
        <CreateChallengeModal t={t} friends={friends}
          onClose={() => setShowCreate(false)}
          onCreated={() => { setShowCreate(false); refresh() }}
        />
      )}
    </div>
  )
}
