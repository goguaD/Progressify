import { useEffect, useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import api from '../api/client'
import AnatomySection from '../components/profile/AnatomySection'
import ProfileActions from '../components/profile/ProfileActions'
import ProfileHeader from '../components/profile/ProfileHeader'
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

  return (
    <div className="profile-page">
      <button className="btn btn-secondary"
        style={{ width: 'auto', padding: '8px 16px', alignSelf: 'flex-start' }}
        onClick={() => navigate(-1)}>
        {t.profile_back}
      </button>

      <ProfileHeader profile={profile} isMe={isMe} t={t} setMe={setMe} onReload={load} />

      {!isMe && (
        <div className="profile-actions">
          <ProfileActions profile={profile} busy={busy} withBusy={withBusy} t={t} />
        </div>
      )}

      <AnatomySection profile={profile} t={t} />
    </div>
  )
}
