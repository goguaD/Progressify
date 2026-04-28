import { useEffect, useRef, useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import api, { resolveAssetUrl } from '../api/client'
import BodyFigure from '../components/BodyFigure'
import { useApp } from '../contexts/AppContext'

export default function Profile() {
  const { username } = useParams()
  const { t } = useApp()
  const navigate = useNavigate()
  const { setUser: setMe } = useOutletContext()

  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [busy, setBusy] = useState(false)
  const [view, setView] = useState('front')
  const [uploading, setUploading] = useState(false)
  const [uploadErr, setUploadErr] = useState('')
  const fileRef = useRef(null)

  async function load() {
    setLoading(true)
    try {
      const { data } = await api.get(`/users/by-username/${username}`)
      setProfile(data)
      setNotFound(false)
    } catch (err) {
      if (err.response?.status === 404) setNotFound(true)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [username])

  async function withBusy(fn) {
    setBusy(true)
    try { await fn() } finally { setBusy(false) }
    load()
  }

  async function onPickFile(e) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    setUploadErr('')

    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
      setUploadErr(t.err_avatar_type)
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setUploadErr(t.err_avatar_size)
      return
    }

    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    try {
      const { data } = await api.post('/me/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      localStorage.setItem('user', JSON.stringify(data))
      setMe?.(data)
      load()
    } catch (err) {
      setUploadErr(err.response?.data?.detail || 'Upload failed.')
    } finally {
      setUploading(false)
    }
  }

  async function onRemoveAvatar() {
    setUploading(true)
    try {
      const { data } = await api.delete('/me/avatar')
      localStorage.setItem('user', JSON.stringify(data))
      setMe?.(data)
      load()
    } catch {
      // silent
    } finally {
      setUploading(false)
    }
  }

  if (loading) return <div className="main-body"><p className="muted">…</p></div>
  if (notFound) {
    return (
      <div className="main-body">
        <h1 className="main-greeting">{t.profile_not_found}</h1>
        <button className="btn btn-secondary" style={{ width: 'auto', padding: '10px 18px' }}
          onClick={() => navigate(-1)}>
          {t.profile_back}
        </button>
      </div>
    )
  }

  const isMe = profile.relationship === 'self'
  const avatarSrc = resolveAssetUrl(profile.avatar_url)
  const initials = ((profile.firstname?.[0] || '') + (profile.lastname?.[0] || '')).toUpperCase() || '?'
  const goalLabel = profile.goal ? (t.goals[profile.goal] || profile.goal) : '—'

  // Friendship action button (same as before, just compacted)
  let actionEl = null
  if (isMe) {
    actionEl = null
  } else if (profile.relationship === 'friends') {
    actionEl = (
      <button className="btn btn-secondary" disabled={busy}
        style={{ width: 'auto', padding: '10px 18px' }}
        onClick={() => withBusy(() => api.delete(`/friends/${profile.id}`))}>
        {t.profile_remove}
      </button>
    )
  } else if (profile.relationship === 'pending_outgoing') {
    actionEl = <span className="badge badge-user">{t.profile_pending_outgoing}</span>
  } else if (profile.relationship === 'pending_incoming') {
    actionEl = (
      <div style={{ display: 'flex', gap: 8 }}>
        <button className="btn btn-primary" disabled={busy}
          style={{ width: 'auto', padding: '10px 18px' }}
          onClick={() => withBusy(() => api.post(`/friends/accept/${profile.pending_request_id}`))}>
          {t.profile_accept}
        </button>
        <button className="btn btn-secondary" disabled={busy}
          style={{ width: 'auto', padding: '10px 18px' }}
          onClick={() => withBusy(() => api.post(`/friends/decline/${profile.pending_request_id}`))}>
          {t.profile_decline}
        </button>
      </div>
    )
  } else {
    actionEl = (
      <button className="btn btn-primary" disabled={busy}
        style={{ width: 'auto', padding: '10px 18px' }}
        onClick={() => withBusy(() => api.post('/friends/request', { username: profile.username }))}>
        {t.profile_add}
      </button>
    )
  }

  return (
    <div className="profile-page">
      <button
        className="btn btn-secondary"
        style={{ width: 'auto', padding: '8px 16px', alignSelf: 'flex-start' }}
        onClick={() => navigate(-1)}
      >
        {t.profile_back}
      </button>

      {/* ── Header card ─────────────────────────────────────── */}
      <div className="profile-header-card">
        <div className="profile-id">
          <div className={`avatar avatar-xl ${profile.is_online ? 'is-online' : ''}`}>
            {avatarSrc
              ? <img src={avatarSrc} alt="" className="avatar-img" />
              : <span>{initials}</span>}
            <span className={`status-dot ${profile.is_online ? 'online' : 'offline'}`} />
          </div>
          <div>
            <h1 className="profile-name" style={{ marginTop: 0 }}>
              {profile.firstname} {profile.lastname}
            </h1>
            <p className="profile-handle">@{profile.username}</p>
            <p className={`profile-online ${profile.is_online ? 'online' : 'offline'}`}>
              {profile.is_online ? t.friends_status_online : t.friends_status_offline}
            </p>
            <div className="profile-meta" style={{ marginTop: 10, justifyContent: 'flex-start' }}>
              {profile.goal && <span className="chip">{goalLabel}</span>}
              {profile.weight && <span className="chip">{profile.weight} kg</span>}
              {profile.height && <span className="chip">{profile.height} cm</span>}
            </div>
          </div>
        </div>

        {/* Stats grid */}
        <div className="profile-stats">
          <ProfileStat label={t.profile_stat_friends} value={profile.friend_count ?? 0} />
          <ProfileStat label={t.profile_stat_workout} value={profile.current_workout || '—'} small />
          <ProfileStat label={t.profile_stat_meal} value={profile.current_meal_plan || '—'} small />
          <ProfileStat label={t.profile_stat_last} value={profile.last_workout_text || t.no_workout_yet} small />
        </div>

        {/* Owner controls / friendship action */}
        <div className="profile-actions">
          {isMe ? (
            <>
              <input
                ref={fileRef}
                type="file"
                accept="image/png,image/jpeg,image/webp"
                style={{ display: 'none' }}
                onChange={onPickFile}
              />
              <button
                className="btn btn-primary"
                style={{ width: 'auto', padding: '10px 18px' }}
                onClick={() => fileRef.current?.click()}
                disabled={uploading}
              >
                {uploading
                  ? t.avatar_uploading
                  : (profile.avatar_url ? t.avatar_change : t.avatar_upload)}
              </button>
              {profile.avatar_url && !uploading && (
                <button
                  className="btn btn-secondary"
                  style={{ width: 'auto', padding: '10px 18px' }}
                  onClick={onRemoveAvatar}
                >
                  {t.avatar_remove}
                </button>
              )}
              {uploadErr && <p className="tiny-msg err">{uploadErr}</p>}
            </>
          ) : actionEl}
        </div>
      </div>

      {/* ── Anatomy card ────────────────────────────────────── */}
      <div className="anatomy-card">
        <div className="anatomy-header">
          <div>
            <h2 className="anatomy-title">{t.profile_anatomy} 🧬</h2>
            <p className="anatomy-sub">{t.profile_anatomy_sub}</p>
          </div>
          <div className="filter-tabs anatomy-tabs" role="tablist">
            {[
              { id: 'front', label: t.profile_view_front },
              { id: 'back',  label: t.profile_view_back  },
            ].map((opt) => (
              <button
                key={opt.id}
                role="tab"
                aria-selected={view === opt.id}
                className={`filter-tab ${view === opt.id ? 'active' : ''}`}
                onClick={() => setView(opt.id)}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>

        <div className="anatomy-figure-wrap">
          <BodyFigure
            gender={profile.gender}
            view={view}
          />
        </div>
      </div>
    </div>
  )
}

function ProfileStat({ label, value, small }) {
  return (
    <div className="profile-stat">
      <div className="profile-stat-label">{label}</div>
      <div className={`profile-stat-value ${small ? 'small' : ''}`}>{value}</div>
    </div>
  )
}
