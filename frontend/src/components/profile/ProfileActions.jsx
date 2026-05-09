import api from '../../api/client'

export default function ProfileActions({ profile, busy, withBusy, t }) {
  if (profile.relationship === 'self') return null

  if (profile.relationship === 'friends') {
    return (
      <button className="btn btn-secondary" disabled={busy}
        style={{ width: 'auto', padding: '10px 18px' }}
        onClick={() => withBusy(() => api.delete(`/friends/${profile.id}`))}>
        {t.profile_remove}
      </button>
    )
  }

  if (profile.relationship === 'pending_outgoing') {
    return <span className="badge badge-user">{t.profile_pending_outgoing}</span>
  }

  if (profile.relationship === 'pending_incoming') {
    return (
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
  }

  return (
    <button className="btn btn-primary" disabled={busy}
      style={{ width: 'auto', padding: '10px 18px' }}
      onClick={() => withBusy(() => api.post('/friends/request', { username: profile.username }))}>
      {t.profile_add}
    </button>
  )
}
