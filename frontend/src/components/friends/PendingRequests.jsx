import { useNavigate } from 'react-router-dom'
import Avatar from './Avatar'

export default function PendingRequests({ pending, accept, decline, t }) {
  const navigate = useNavigate()

  return (
    <div className="side-card">
      <p className="side-card-title">
        {t.friends_pending_section} {pending.length > 0 && <span className="pill">{pending.length}</span>}
      </p>
      {pending.length === 0 && <p className="muted">{t.friends_no_pending}</p>}
      {pending.map((req) => (
        <div key={req.id} className="pending-row">
          <button
            type="button"
            className="pending-info"
            onClick={() => navigate(`/u/${req.requester.username}`)}
          >
            <Avatar user={req.requester} small />
            <div>
              <div className="search-row-name">@{req.requester.username}</div>
              <div className="search-row-sub">
                {req.requester.firstname} {req.requester.lastname}
              </div>
            </div>
          </button>
          <div className="pending-actions">
            <button className="btn btn-primary btn-tiny" onClick={() => accept(req.id)}>
              {t.friends_accept}
            </button>
            <button className="btn btn-secondary btn-tiny" onClick={() => decline(req.id)}>
              {t.friends_decline}
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}
