import { useState, useEffect, useRef, useCallback } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import api, { resolveAssetUrl } from '../api/client'
import { useApp } from '../contexts/AppContext'
import Controls from './Controls'

const POLL_MS = 30_000

function timeAgoShort(isoString) {
  if (!isoString) return ''
  const diff = Date.now() - new Date(isoString).getTime()
  const m = Math.floor(diff / 60000)
  if (m < 2) return 'now'
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h`
  return `${Math.floor(h / 24)}d`
}

function NotifItem({ notif, t, onNavigate }) {
  const LEVEL_COLORS = {
    beginner: '#60a5fa',
    intermediate: '#a78bfa',
    advanced: '#f97316',
    elite: '#ef4444',
  }

  function label() {
    switch (notif.type) {
      case 'friend_request':
        return (
          <span>
            <strong>@{notif.from_user?.username}</strong>{' '}
            {t.notif_friend_request}
          </span>
        )
      case 'challenge_received': {
        const typeKey = `ch_type_${notif.challenge_type}`
        return (
          <span>
            <strong>@{notif.from_user?.username}</strong>{' '}
            {t.notif_challenge_received}{' '}
            <em>({t[typeKey] || notif.challenge_type})</em>
          </span>
        )
      }
      case 'challenge_completed': {
        const winner = notif.winner
        return (
          <span>
            <strong>@{notif.challenger?.username}</strong> vs{' '}
            <strong>@{notif.opponent?.username}</strong>{' '}
            — {t.notif_challenge_completed}
            {winner && <em> 🏆 {winner.firstname}</em>}
          </span>
        )
      }
      case 'friend_pr': {
        const col = notif.level ? LEVEL_COLORS[notif.level] : 'var(--accent)'
        return (
          <span>
            <strong>@{notif.user?.username}</strong>{' '}
            {t.notif_friend_pr}:{' '}
            <em style={{ color: col }}>{notif.exercise_name} — {notif.weight_kg} kg</em>
          </span>
        )
      }
      case 'muscle_achievement': {
        const musKey = `muscle_${(notif.muscle_slug || '').replace('-', '_')}`
        const lvlKey = `level_${notif.new_level}`
        const col = LEVEL_COLORS[notif.new_level] || 'var(--accent)'
        return (
          <span>
            <strong>@{notif.user?.username}</strong>{' '}
            {t.notif_muscle_achievement}{' '}
            <em style={{ color: col }}>{t[lvlKey] || notif.new_level}</em>{' '}
            ({t[musKey] || notif.muscle_slug})
          </span>
        )
      }
      case 'report':
        return (
          <span>
            <strong>@{notif.reporter_username}</strong>{' '}
            {t.notif_report}{' '}
            <em>{notif.target_type}: {notif.target_name}</em>
            {' — '}<em>{notif.reason}</em>
          </span>
        )
      default:
        return <span>{notif.type}</span>
    }
  }

  return (
    <button
      className="notif-item"
      onClick={() => onNavigate(notif.link || '/')}
    >
      <span className="notif-item-icon">
        {notif.type === 'friend_request' && '👤'}
        {notif.type === 'challenge_received' && '⚔️'}
        {notif.type === 'challenge_completed' && '🏆'}
        {notif.type === 'friend_pr' && '💪'}
        {notif.type === 'muscle_achievement' && '🧬'}
        {notif.type === 'report' && '🚨'}
      </span>
      <span className="notif-item-body">{label()}</span>
      <span className="notif-item-time">{timeAgoShort(notif.timestamp)}</span>
    </button>
  )
}

export default function Header({ user, onLogout }) {
  const { t } = useApp()
  const navigate = useNavigate()

  const [notifications, setNotifications] = useState([])
  const [open, setOpen] = useState(false)
  const [lastSeen, setLastSeen] = useState(
    () => localStorage.getItem('notifLastSeen') || ''
  )
  const dropRef = useRef(null)
  const bellRef = useRef(null)

  const fetchNotifications = useCallback(async () => {
    try {
      const { data } = await api.get('/notifications')
      setNotifications(data.notifications || [])
    } catch {
      /* silently fail */
    }
  }, [])

  useEffect(() => {
    fetchNotifications()
    const id = setInterval(fetchNotifications, POLL_MS)
    return () => clearInterval(id)
  }, [fetchNotifications])

  // Close dropdown when clicking outside
  useEffect(() => {
    if (!open) return
    function handleClick(e) {
      if (
        dropRef.current && !dropRef.current.contains(e.target) &&
        bellRef.current && !bellRef.current.contains(e.target)
      ) {
        setOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [open])

  const unreadCount = notifications.filter(
    (n) => !lastSeen || new Date(n.timestamp) > new Date(lastSeen)
  ).length

  function handleBellClick() {
    if (!open) {
      const now = new Date().toISOString()
      setLastSeen(now)
      localStorage.setItem('notifLastSeen', now)
    }
    setOpen((v) => !v)
  }

  function handleNotifNavigate(link) {
    setOpen(false)
    navigate(link)
  }

  const navItems = [
    { to: '/',            label: t.nav_home },
    { to: '/mealplans',   label: t.nav_mealplans },
    { to: '/workouts',    label: t.nav_workouts },
    { to: '/friends',     label: t.nav_friends },
    { to: '/challenges',  label: t.nav_challenges },
    ...(user?.role === 'admin' ? [{ to: '/admin', label: t.admin_nav || '⚡ Admin' }] : []),
  ]

  const initials = ((user?.firstname?.[0] || '') + (user?.lastname?.[0] || '')).toUpperCase() || '?'
  const avatarSrc = resolveAssetUrl(user?.avatar_url)

  return (
    <nav className="main-nav app-header">
      <div
        className="brand"
        style={{ margin: 0, cursor: 'pointer' }}
        onClick={() => navigate('/')}
      >
        <div className="brand-icon">💪</div>
        <div className="brand-name">Pro<span>gressify</span></div>
      </div>

      <div className="app-header-links">
        {navItems.map((n) => (
          <NavLink
            key={n.to}
            to={n.to}
            end={n.to === '/'}
            className={({ isActive }) =>
              'app-header-link' + (isActive ? ' active' : '')
            }
          >
            {n.label}
          </NavLink>
        ))}
      </div>

      <div className="app-header-right">
        <Controls inline />

        {/* ── Notification bell ──────────────────────────────── */}
        <div className="notif-wrap">
          <button
            ref={bellRef}
            className={`notif-bell-btn${open ? ' active' : ''}`}
            onClick={handleBellClick}
            aria-label="Notifications"
          >
            🔔
            {unreadCount > 0 && (
              <span className="notif-badge">
                {unreadCount > 99 ? '99+' : unreadCount}
              </span>
            )}
          </button>

          {open && (
            <div ref={dropRef} className="notif-dropdown">
              <div className="notif-dropdown-header">
                <span className="notif-dropdown-title">{t.notif_title}</span>
                {notifications.length > 0 && (
                  <button
                    className="notif-mark-read"
                    onClick={() => {
                      const now = new Date().toISOString()
                      setLastSeen(now)
                      localStorage.setItem('notifLastSeen', now)
                    }}
                  >
                    {t.notif_mark_read}
                  </button>
                )}
              </div>

              <div className="notif-dropdown-body">
                {notifications.length === 0 ? (
                  <div className="notif-empty">
                    <span className="notif-empty-icon">🔕</span>
                    <p>{t.notif_empty}</p>
                    <p className="notif-empty-sub">{t.notif_empty_sub}</p>
                  </div>
                ) : (
                  notifications.map((n) => (
                    <NotifItem
                      key={n.id}
                      notif={n}
                      t={t}
                      onNavigate={handleNotifNavigate}
                    />
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {user && (
          <button
            type="button"
            className="header-profile-btn"
            onClick={() => navigate(`/u/${user.username}`)}
            title={t.profile_my}
          >
            <span className="header-avatar">
              {avatarSrc ? (
                <img src={avatarSrc} alt="" />
              ) : (
                <span>{initials}</span>
              )}
            </span>
            <span className="header-username">@{user.username}</span>
          </button>
        )}

        {user && (
          <span className={`badge ${user.role === 'admin' ? 'badge-admin' : 'badge-user'}`}>
            {user.role === 'admin' ? t.badge_admin : t.badge_user}
          </span>
        )}

        <button
          className="btn btn-secondary"
          onClick={onLogout}
          style={{ width: 'auto', padding: '8px 16px', fontSize: 13 }}
        >
          {t.logout}
        </button>
      </div>
    </nav>
  )
}
