import { useEffect, useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import api from '../api/client'
import AnatomySection from '../components/profile/AnatomySection'
import BMIGauge from '../components/profile/BMIGauge'
import MyWorkoutPlan from '../components/profile/MyWorkoutPlan'
import ProfileActions from '../components/profile/ProfileActions'
import ProfileHeader from '../components/profile/ProfileHeader'
import AddPlanToProfileModal from '../components/workouts/AddPlanToProfileModal'
import { useApp } from '../contexts/AppContext'


export default function Profile() {
  const { username } = useParams()
  const { t, lang } = useApp()
  const navigate = useNavigate()
  const { setUser: setMe } = useOutletContext()

  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [notFound, setNotFound] = useState(false)
  const [busy, setBusy] = useState(false)
  const [editLifts, setEditLifts] = useState(null)

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

  async function openUpdateLifts() {
    if (!profile?.active_workout?.plan?.id) return
    try {
      const { data } = await api.get(`/workouts/${profile.active_workout.plan.id}`)
      setEditLifts({ plan: data, mode: 'update' })
    } catch { /* ignore */ }
  }

  async function removeActivePlan() {
    if (!confirm(t.profile_remove_confirm || 'Remove this plan from your profile?')) return
    try {
      await api.delete('/me/workout-plan')
      load()
    } catch { /* ignore */ }
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
  const activePlan = profile.active_workout?.plan
  const initialLifts = (profile.active_workout?.lifts || []).reduce((acc, l) => {
    acc[l.exercise_name] = l.weight_kg
    return acc
  }, {})

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

      <BMIGauge
        weight={profile.weight}
        height={profile.height}
        age={profile.age}
        t={t}
      />

      <AnatomySection
        profile={profile}
        t={t}
        editable={isMe && !!activePlan}
        onUpdateLifts={openUpdateLifts}
      />

      {isMe && (
        <MyWorkoutPlan
          plan={activePlan}
          t={t}
          appLang={lang}
          editable
          onChange={() => navigate('/workouts')}
          onUpdate={openUpdateLifts}
          onRemove={activePlan ? removeActivePlan : undefined}
        />
      )}

      {editLifts && (
        <AddPlanToProfileModal
          plan={editLifts.plan}
          mode={editLifts.mode}
          initialLifts={initialLifts}
          t={t}
          appLang={lang}
          onClose={() => setEditLifts(null)}
          onSaved={() => { setEditLifts(null); load() }}
        />
      )}
    </div>
  )
}
