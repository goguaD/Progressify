import { useNavigate } from 'react-router-dom'
import Avatar from './Avatar'

export default function FriendSearch({ search, setSearch, results, searching, actionMsg, setActionMsg, sendRequest, t }) {
  const navigate = useNavigate()

  return (
    <div className="side-card">
      <p className="side-card-title">{t.friends_add}</p>
      <div className="search-box">
        <input
          value={search}
          onChange={(e) => { setSearch(e.target.value); setActionMsg(null) }}
          placeholder={t.friends_add_ph}
          style={{ marginBottom: 0 }}
        />
      </div>

      {actionMsg && (
        <p className={`tiny-msg ${actionMsg.type === 'ok' ? 'ok' : 'err'}`}>
          {actionMsg.text}
        </p>
      )}

      {search && (
        <div className="search-results">
          {searching && <p className="muted">…</p>}
          {!searching && results.length === 0 && (
            <p className="muted">{t.friends_search_empty}</p>
          )}
          {results.map((u) => (
            <div key={u.id} className="search-row">
              <button
                type="button"
                className="search-row-info"
                onClick={() => navigate(`/u/${u.username}`)}
              >
                <Avatar user={u} small />
                <div>
                  <div className="search-row-name">@{u.username}</div>
                  <div className="search-row-sub">
                    {u.firstname} {u.lastname}
                  </div>
                </div>
              </button>
              <button
                className="btn btn-primary btn-tiny"
                onClick={() => sendRequest(u.username)}
              >
                {t.friends_add_btn}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
