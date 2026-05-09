import { NavLink, useNavigate } from 'react-router-dom'
import { resolveAssetUrl } from '../api/client'
import { useApp } from '../contexts/AppContext'
import Controls from './Controls'

export default function Header({ user, onLogout }) {
  const { t } = useApp()
  const navigate = useNavigate()

  const navItems = [
    { to: '/',            label: t.nav_home },
    { to: '/mealplans',   label: t.nav_mealplans },
    { to: '/workouts',    label: t.nav_workouts },
    { to: '/friends',     label: t.nav_friends },
    { to: '/challenges',  label: t.nav_challenges },
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
