import { useRef, useState } from 'react'
import api, { resolveAssetUrl } from '../../api/client'

export default function ProfileHeader({ profile, isMe, t, setMe, onReload }) {
  const [uploading, setUploading] = useState(false)
  const [uploadErr, setUploadErr] = useState('')
  const fileRef = useRef(null)

  const avatarSrc = resolveAssetUrl(profile.avatar_url)
  const initials = ((profile.firstname?.[0] || '') + (profile.lastname?.[0] || '')).toUpperCase() || '?'
  const goalLabel = profile.goal ? (t.goals[profile.goal] || profile.goal) : '—'

  async function onPickFile(e) {
    const file = e.target.files?.[0]
    e.target.value = ''
    if (!file) return
    setUploadErr('')

    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
      setUploadErr(t.err_avatar_type); return
    }
    if (file.size > 5 * 1024 * 1024) {
      setUploadErr(t.err_avatar_size); return
    }

    const formData = new FormData()
    formData.append('file', file)
    setUploading(true)
    try {
      const { data } = await api.post('/me/avatar', formData)
      localStorage.setItem('user', JSON.stringify(data))
      setMe?.(data)
      onReload()
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
      onReload()
    } catch {
    } finally {
      setUploading(false)
    }
  }

  return (
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

      <div className="profile-stats">
        <ProfileStat label={t.profile_stat_friends} value={profile.friend_count ?? 0} />
        <ProfileStat label={t.profile_stat_workout} value={profile.current_workout || '—'} small />
        <ProfileStat label={t.profile_stat_meal} value={profile.current_meal_plan || '—'} small />
        <ProfileStat label={t.profile_stat_last} value={profile.last_workout_text || t.no_workout_yet} small />
      </div>

      <div className="profile-actions">
        {isMe ? (
          <>
            <input ref={fileRef} type="file" accept="image/png,image/jpeg,image/webp"
              style={{ display: 'none' }} onChange={onPickFile} />
            <button className="btn btn-primary" style={{ width: 'auto', padding: '10px 18px' }}
              onClick={() => fileRef.current?.click()} disabled={uploading}>
              {uploading
                ? t.avatar_uploading
                : (profile.avatar_url ? t.avatar_change : t.avatar_upload)}
            </button>
            {profile.avatar_url && !uploading && (
              <button className="btn btn-secondary" style={{ width: 'auto', padding: '10px 18px' }}
                onClick={onRemoveAvatar}>
                {t.avatar_remove}
              </button>
            )}
            {uploadErr && <p className="tiny-msg err">{uploadErr}</p>}
          </>
        ) : null}
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
