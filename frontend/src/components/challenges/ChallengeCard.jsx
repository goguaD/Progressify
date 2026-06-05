import { useEffect, useState } from 'react'
import api from '../../api/client'
import ChallengeAvatar from './ChallengeAvatar'

export default function ChallengeCard({ ch, t, navigate, onRefresh }) {
  const me = JSON.parse(localStorage.getItem('user') || '{}')
  const iAmOpponent = ch.opponent.id === me.id
  const [showSubmit, setShowSubmit] = useState(false)
  const [value, setValue] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [busy, setBusy] = useState(false)
  const [reveal, setReveal] = useState(0)

  const typeLabel = t[`ch_type_${ch.challenge_type}`] || ch.challenge_type
  const deadlineStr = ch.deadline ? new Date(ch.deadline).toLocaleString() : '—'

  const statusClass = ch.status === 'accepted' ? 'active' :
    ch.status === 'completed' ? 'completed' :
    ch.status === 'declined' ? 'declined' : 'pending'

  useEffect(() => {
    if (ch.status !== 'completed' || !ch.my_result) return
    const t1 = setTimeout(() => setReveal(1), 300)
    const t2 = setTimeout(() => setReveal(2), 900)
    const t3 = setTimeout(() => setReveal(3), 1500)
    return () => { clearTimeout(t1); clearTimeout(t2); clearTimeout(t3) }
  }, [ch.status, ch.my_result])

  async function accept() {
    setBusy(true); try { await api.post(`/challenges/${ch.id}/accept`) } catch {} setBusy(false); onRefresh()
  }
  async function decline() {
    setBusy(true); try { await api.post(`/challenges/${ch.id}/decline`) } catch {} setBusy(false); onRefresh()
  }
  async function submitResult() {
    const num = parseFloat(value)
    if (isNaN(num) || num < 0) return
    setSubmitting(true)
    try { await api.post(`/challenges/${ch.id}/submit`, { value: num }); setShowSubmit(false); setValue('') } catch {}
    setSubmitting(false); onRefresh()
  }

  function resultUnit() {
    if (ch.challenge_type === 'strength') return t.ch_result_kg
    if (ch.challenge_type === 'endurance') return t.ch_result_sec
    return t.ch_result_kg
  }

  function formatResult(v) {
    if (v == null) return t.ch_auto_loss
    if (ch.challenge_type === 'endurance') {
      const mins = Math.floor(v / 60)
      const secs = Math.round(v % 60)
      return `${mins}m ${secs}s`
    }
    return `${v} ${resultUnit()}`
  }

  function typeDetail() {
    const parts = []
    if (ch.challenge_type === 'strength' && ch.muscle_group) {
      const key = `muscle_${ch.muscle_group.replace('-', '_')}`
      parts.push(t[key] || ch.muscle_group)
    }
    if (ch.challenge_type === 'endurance') {
      if (ch.endurance_mode) parts.push(t[`ch_mode_${ch.endurance_mode}`] || ch.endurance_mode)
      if (ch.endurance_speed) parts.push(`${ch.endurance_speed} km/h`)
      if (ch.endurance_gradient != null && ch.endurance_mode === 'treadmill') parts.push(`${ch.endurance_gradient}%`)
    }
    if (ch.challenge_type === 'target_weight' && ch.target_weight_kg) {
      parts.push(`${t.ch_goal}: ${ch.target_weight_kg} kg`)
    }
    return parts.length ? parts.join(' · ') : null
  }

  function submitLabel() {
    if (ch.challenge_type === 'strength') return t.ch_submit_kg
    if (ch.challenge_type === 'endurance') return t.ch_submit_time
    return t.ch_submit_weight
  }

  const detail = typeDetail()

  return (
    <div className={`challenge-card challenge-card--${statusClass}`}>
      <div className="challenge-card-top">
        <div className="challenge-card-users">
          <button className="challenge-user" onClick={() => navigate(`/u/${ch.challenger.username}`)}>
            <ChallengeAvatar user={ch.challenger} />
            <span className="challenge-user-name">
              {ch.challenger.id === me.id ? t.ch_you : ch.challenger.firstname}
            </span>
          </button>
          <span className="challenge-vs">{t.ch_vs}</span>
          <button className="challenge-user" onClick={() => navigate(`/u/${ch.opponent.username}`)}>
            <ChallengeAvatar user={ch.opponent} />
            <span className="challenge-user-name">
              {ch.opponent.id === me.id ? t.ch_you : ch.opponent.firstname}
            </span>
          </button>
        </div>
        <div className="challenge-card-info">
          <span className={`challenge-status-badge challenge-status--${statusClass}`}>
            {t[`ch_${ch.status === 'accepted' ? 'active' : ch.status}`] || ch.status}
          </span>
          <span className="challenge-type-badge">{typeLabel}</span>
        </div>
      </div>

      {detail && <p className="challenge-detail">{detail}</p>}
      {ch.message && <p className="challenge-message">"{ch.message}"</p>}

      <div className="challenge-meta">
        {ch.deadline && <span>⏰ {deadlineStr}</span>}
        {ch.challenge_type === 'target_weight' && <span>🎯 {t.ch_first_wins}</span>}
        {ch.deadline_soon && <span className="challenge-deadline-warn">{t.ch_deadline_soon}</span>}
      </div>

      {ch.status === 'pending' && iAmOpponent && (
        <div className="challenge-actions">
          <button className="btn btn-primary btn-tiny" disabled={busy} onClick={accept}>{t.ch_accept}</button>
          <button className="btn btn-secondary btn-tiny" disabled={busy} onClick={decline}>{t.ch_decline}</button>
        </div>
      )}
      {ch.status === 'pending' && !iAmOpponent && (
        <p className="challenge-waiting muted">{t.ch_waiting}</p>
      )}

      {ch.status === 'accepted' && !ch.my_submitted && !showSubmit && (
        <button className="btn btn-primary btn-tiny" style={{ marginTop: 8 }}
          onClick={() => setShowSubmit(true)}>{t.ch_submit}</button>
      )}

      {ch.status === 'accepted' && showSubmit && !ch.my_submitted && (
        <div className="challenge-submit-row">
          <label className="challenge-submit-label">{submitLabel()}</label>
          <input type="number" min="0" step="any" value={value}
            onChange={(e) => setValue(e.target.value)}
            className="challenge-result-input" />
          <button className="btn btn-primary btn-tiny"
            disabled={submitting || !value || parseFloat(value) < 0}
            onClick={submitResult}>{submitting ? '…' : t.ch_submit}</button>
          <button className="btn btn-secondary btn-tiny"
            onClick={() => setShowSubmit(false)}>{t.ch_cancel}</button>
        </div>
      )}

      {ch.status === 'accepted' && ch.my_submitted && (
        <p className="challenge-submitted-msg">{t.ch_you_submitted}</p>
      )}
      {ch.status === 'accepted' && ch.my_submitted && !ch.their_submitted && (
        <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>{t.ch_waiting}</p>
      )}

      {ch.status === 'completed' && (
        <div className="challenge-results">
          <div className={`challenge-result-col reveal-step ${reveal >= 1 ? 'visible' : ''}`}>
            <span className="challenge-result-who">
              {ch.challenger.id === me.id ? t.ch_you : ch.challenger.firstname}
            </span>
            <span className="challenge-result-val">
              {formatResult(ch.challenger.id === me.id ? ch.my_result : ch.their_result)}
            </span>
          </div>
          <div className={`challenge-result-col reveal-step ${reveal >= 2 ? 'visible' : ''}`}>
            <span className="challenge-result-who">
              {ch.opponent.id === me.id ? t.ch_you : ch.opponent.firstname}
            </span>
            <span className="challenge-result-val">
              {formatResult(ch.opponent.id === me.id ? ch.my_result : ch.their_result)}
            </span>
          </div>
          <div className={`challenge-winner-wrap reveal-step ${reveal >= 3 ? 'visible' : ''}`}>
            {ch.winner ? (
              <div className="challenge-winner">
                🏆 {t.ch_winner}: {ch.winner.id === me.id ? t.ch_you : ch.winner.firstname}
              </div>
            ) : (ch.my_result != null && ch.their_result != null) ? (
              <div className="challenge-winner">{t.ch_draw}</div>
            ) : null}
          </div>
        </div>
      )}
    </div>
  )
}
