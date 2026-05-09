import Avatar from './Avatar'

export default function FriendCard({ friend, t, onClick, onRemoveClick, onChallenge, h2h }) {
  const goalLabel = friend.goal ? (t.goals[friend.goal] || friend.goal) : '—'

  return (
    <div className="friend-card">
      <button type="button" className="friend-card-main" onClick={onClick}>
        <Avatar user={friend} />
        <div className="friend-card-text">
          <div className="friend-card-top">
            <span className="friend-card-name">{friend.firstname} {friend.lastname}</span>
            <span className={`friend-status ${friend.is_online ? 'online' : 'offline'}`}>
              {friend.is_online ? t.friends_status_online : t.friends_status_offline}
            </span>
          </div>
          <div className="friend-card-handle">@{friend.username} · {goalLabel}</div>
          <div className="friend-card-meta">
            <span><b>{t.friends_workout}:</b> {friend.current_workout || '—'}</span>
            <span><b>{t.friends_meal}:</b> {friend.current_meal_plan || '—'}</span>
          </div>
          {friend.last_activity && (
            <div className="friend-card-activity">{friend.last_activity}</div>
          )}
        </div>
      </button>

      <div className="friend-card-actions">
        {h2h && (h2h.wins > 0 || h2h.losses > 0 || h2h.draws > 0) && (
          <span className="h2h-badge" title={t.ch_h2h}>
            {t.ch_h2h} {h2h.wins}{t.ch_wins}-{h2h.losses}{t.ch_losses}-{h2h.draws}{t.ch_draws}
          </span>
        )}
        <button
          type="button"
          className="btn btn-primary btn-tiny"
          onClick={(e) => { e.stopPropagation(); onChallenge() }}
        >
          ⚔️ {t.ch_challenge}
        </button>
        <button
          type="button"
          className="btn btn-danger btn-tiny friend-remove-btn"
          onClick={(e) => { e.stopPropagation(); onRemoveClick() }}
        >
          {t.friends_remove_btn}
        </button>
      </div>
    </div>
  )
}
