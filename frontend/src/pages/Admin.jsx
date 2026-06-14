import { useState, useEffect, useCallback } from 'react'
import { useOutletContext, useNavigate } from 'react-router-dom'
import api from '../api/client'
import { useApp } from '../contexts/AppContext'

const TABS = ['users', 'reports']

export default function Admin() {
  const { t } = useApp()
  const { user } = useOutletContext()
  const navigate = useNavigate()

  const [tab, setTab] = useState('users')

  // ── Users tab ─────────────────────────────────────────────────────────────
  const [users, setUsers] = useState([])
  const [usersLoading, setUsersLoading] = useState(false)

  // ── Reports tab ───────────────────────────────────────────────────────────
  const [reports, setReports] = useState([])
  const [reportsLoading, setReportsLoading] = useState(false)

  // Redirect non-admins immediately
  useEffect(() => {
    if (user && user.role !== 'admin') navigate('/', { replace: true })
  }, [user, navigate])

  const fetchUsers = useCallback(async () => {
    setUsersLoading(true)
    try {
      const { data } = await api.get('/admin/users')
      setUsers(data)
    } catch {
      /* silently fail */
    } finally {
      setUsersLoading(false)
    }
  }, [])

  const fetchReports = useCallback(async () => {
    setReportsLoading(true)
    try {
      const { data } = await api.get('/admin/reports')
      setReports(data)
    } catch {
      /* silently fail */
    } finally {
      setReportsLoading(false)
    }
  }, [])

  useEffect(() => {
    if (tab === 'users') fetchUsers()
    if (tab === 'reports') fetchReports()
  }, [tab, fetchUsers, fetchReports])

  async function handleDeleteUser(uid) {
    if (!window.confirm(t.admin_delete_confirm || 'Delete this user?')) return
    try {
      await api.delete(`/admin/users/${uid}`)
      setUsers((prev) => prev.filter((u) => u.id !== uid))
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to delete user.')
    }
  }

  async function handleDeleteContent(report) {
    if (!window.confirm(t.admin_delete_confirm || 'Delete this content?')) return
    try {
      if (report.target_type === 'meal') {
        await api.delete(`/admin/meals/${report.target_id}`)
      } else {
        await api.delete(`/admin/workouts/${report.target_id}`)
      }
      await api.patch(`/admin/reports/${report.id}/reviewed`)
      setReports((prev) => prev.filter((r) => r.id !== report.id))
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to delete content.')
    }
  }

  async function handleDismissReport(reportId) {
    try {
      await api.patch(`/admin/reports/${reportId}/reviewed`)
      setReports((prev) => prev.filter((r) => r.id !== reportId))
    } catch {
      /* silently fail */
    }
  }

  if (!user || user.role !== 'admin') return null

  return (
    <div className="admin-page">
      <div className="admin-page-header">
        <h1 className="admin-page-title">⚡ {t.admin_title || 'Admin Panel'}</h1>
        <span className="testing-tag">{t.admin_testing || 'ADMIN'}</span>
      </div>

      {/* ── Tabs ────────────────────────────────────────────────────── */}
      <div className="admin-tabs">
        <button
          className={`admin-tab-btn${tab === 'users' ? ' active' : ''}`}
          onClick={() => setTab('users')}
        >
          👥 {t.admin_tab_users || 'Users'}
        </button>
        <button
          className={`admin-tab-btn${tab === 'reports' ? ' active' : ''}`}
          onClick={() => setTab('reports')}
        >
          🚨 {t.admin_tab_reports || 'Reports'}
          {reports.length > 0 && tab !== 'reports' && (
            <span className="admin-tab-badge">{reports.length}</span>
          )}
        </button>
      </div>

      {/* ── Users tab ───────────────────────────────────────────────── */}
      {tab === 'users' && (
        <div className="admin-tab-content">
          {usersLoading ? (
            <p className="admin-loading-text">{t.admin_loading}</p>
          ) : (
            <div className="admin-table-wrap">
              <table className="admin-table">
                <thead>
                  <tr>
                    {[t.col_id, t.col_username, t.col_name, t.col_email, t.col_role, t.col_goal, t.col_wh, t.col_actions || 'Actions'].map(
                      (h) => <th key={h}>{h}</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id}>
                      <td>{u.id}</td>
                      <td>@{u.username}</td>
                      <td>{u.firstname} {u.lastname}</td>
                      <td>{u.email}</td>
                      <td>
                        <span className={`badge ${u.role === 'admin' ? 'badge-admin' : 'badge-user'}`} style={{ fontSize: 10 }}>
                          {u.role}
                        </span>
                      </td>
                      <td>{u.goal ? (t.goals?.[u.goal] || u.goal) : '—'}</td>
                      <td style={{ whiteSpace: 'nowrap' }}>
                        {u.weight ? `${u.weight}kg` : '—'} / {u.height ? `${u.height}cm` : '—'}
                      </td>
                      <td>
                        {u.role !== 'admin' && (
                          <button
                            className="admin-delete-btn"
                            onClick={() => handleDeleteUser(u.id)}
                            title={t.admin_delete || 'Delete'}
                          >
                            🗑️
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* ── Reports tab ─────────────────────────────────────────────── */}
      {tab === 'reports' && (
        <div className="admin-tab-content">
          {reportsLoading ? (
            <p className="admin-loading-text">{t.admin_loading}</p>
          ) : reports.length === 0 ? (
            <p className="admin-empty-text">✅ {t.admin_reports_empty || 'No pending reports.'}</p>
          ) : (
            <div className="admin-reports-list">
              {reports.map((rep) => (
                <div key={rep.id} className="admin-report-card">
                  <div className="admin-report-meta">
                    <span className="admin-report-type">
                      {rep.target_type === 'meal' ? '🥗' : '🏋️'} {rep.target_type}
                    </span>
                    <span className="admin-report-name">{rep.target_name}</span>
                    <span className="admin-report-id">#{rep.target_id}</span>
                  </div>
                  <div className="admin-report-reason">
                    <strong>{rep.reason}</strong>
                    {rep.notes && <p className="admin-report-notes">{rep.notes}</p>}
                  </div>
                  <div className="admin-report-footer">
                    <span className="admin-report-reporter">
                      Reported by <strong>@{rep.reporter_username}</strong>
                    </span>
                    <span className="admin-report-time">
                      {rep.created_at ? new Date(rep.created_at).toLocaleDateString() : ''}
                    </span>
                  </div>
                  <div className="admin-report-actions">
                    <button
                      className="admin-delete-btn admin-delete-btn--full"
                      onClick={() => handleDeleteContent(rep)}
                    >
                      🗑️ {t.admin_delete || 'Delete'} {rep.target_type}
                    </button>
                    <button
                      className="admin-dismiss-btn"
                      onClick={() => handleDismissReport(rep.id)}
                    >
                      ✓ {t.admin_dismiss_report || 'Dismiss'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
