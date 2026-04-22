import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useApp } from '../contexts/AppContext'
import Controls from '../components/Controls'

export default function Main() {
  const navigate = useNavigate()
  const { t } = useApp()
  const [user, setUser] = useState(null)
  const [adminUsers, setAdminUsers] = useState([])
  const [showAdmin, setShowAdmin] = useState(false)
  const [adminLoading, setAdminLoading] = useState(false)

  useEffect(() => {
    const stored = localStorage.getItem('user')
    if (stored) setUser(JSON.parse(stored))
  }, [])

  function handleLogout() {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  async function fetchAdminUsers() {
    setAdminLoading(true)
    try {
      const token = localStorage.getItem('token')
      const { data } = await api.get(`/admin/users?token=${token}`)
      setAdminUsers(data)
      setShowAdmin(true)
    } catch {
      alert('Failed to fetch admin data.')
    } finally {
      setAdminLoading(false)
    }
  }

  if (!user) return null

  const goalLabel = user.goal ? (t.goals[user.goal] || user.goal) : '—'

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', transition: 'background 0.25s' }}>
      {/* Nav */}
      <nav className="main-nav">
        <div className="brand" style={{ margin: 0 }}>
          <div className="brand-icon">💪</div>
          <div className="brand-name">Pro<span>gressify</span></div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Controls inline />

          <span className={`badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}`}>
            {user.role === 'admin' ? t.badge_admin : t.badge_user}
          </span>

          <button
            className="btn btn-secondary"
            onClick={handleLogout}
            style={{ width: 'auto', padding: '8px 16px', fontSize: 13 }}
          >
            {t.logout}
          </button>
        </div>
      </nav>

      {/* Body */}
      <div className="main-body">
        {/* Hero */}
        <div style={{ textAlign: 'center' }}>
          <p style={{
            fontSize: 12,
            color: 'var(--accent)',
            fontWeight: 700,
            letterSpacing: '0.1em',
            textTransform: 'uppercase',
            marginBottom: 10,
          }}>
            {t.main_welcome}
          </p>
          <h1 className="main-greeting">
            {t.main_hello}, <span>{user.firstname}</span>! 👋
          </h1>
          <p className="main-sub" style={{ marginTop: 10 }}>
            {t.main_soon}
          </p>
        </div>

        {/* Profile card */}
        <div className="info-card">
          <p className="info-card-label">{t.main_profile}</p>
          <div className="info-grid">
            <InfoRow label={t.name} value={`${user.firstname} ${user.lastname}`} />
            <InfoRow label={t.email} value={user.email} />
            {user.weight && <InfoRow label={t.weight} value={`${user.weight} kg`} />}
            {user.height && <InfoRow label={t.height} value={`${user.height} cm`} />}
            {user.goal && <InfoRow label={t.goal} value={goalLabel} />}
          </div>
        </div>

        {/* Admin Panel */}
        {user.role === 'admin' && (
          <div style={{ width: '100%', maxWidth: 860 }}>
            <button
              className="btn btn-secondary"
              onClick={showAdmin ? () => setShowAdmin(false) : fetchAdminUsers}
              disabled={adminLoading}
              style={{ width: 'auto', padding: '10px 18px', fontSize: 13 }}
            >
              {adminLoading ? t.admin_loading : showAdmin ? t.admin_hide : t.admin_open}
            </button>

            {showAdmin && (
              <div className="admin-panel" style={{ marginTop: 14 }}>
                <div className="admin-panel-header">
                  <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--accent)' }}>
                    ⚡ {t.admin_title} ({adminUsers.length})
                  </span>
                  <span className="testing-tag">{t.admin_testing}</span>
                </div>
                <table className="admin-table">
                  <thead>
                    <tr>
                      {[t.col_id, t.col_name, t.col_email, t.col_role, t.col_goal, t.col_wh, t.col_hash].map(
                        (h) => <th key={h}>{h}</th>
                      )}
                    </tr>
                  </thead>
                  <tbody>
                    {adminUsers.map((u) => (
                      <tr key={u.id}>
                        <td>{u.id}</td>
                        <td>{u.firstname} {u.lastname}</td>
                        <td>{u.email}</td>
                        <td>
                          <span className={`badge ${u.role === 'admin' ? 'badge-admin' : 'badge-user'}`}
                            style={{ fontSize: 10 }}>
                            {u.role}
                          </span>
                        </td>
                        <td>{u.goal ? (t.goals[u.goal] || u.goal) : '—'}</td>
                        <td style={{ whiteSpace: 'nowrap' }}>
                          {u.weight ? `${u.weight}kg` : '—'} / {u.height ? `${u.height}cm` : '—'}
                        </td>
                        <td className="hash-cell">{u.password_hash}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        <p className="coming-soon-text">{t.coming_soon}</p>
      </div>
    </div>
  )
}

function InfoRow({ label, value }) {
  return (
    <div>
      <p className="info-row-label">{label}</p>
      <p className="info-row-value">{value}</p>
    </div>
  )
}
