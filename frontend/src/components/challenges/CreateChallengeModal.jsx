import { useEffect, useState } from 'react'
import api from '../../api/client'

const TYPES = ['strength', 'endurance', 'target_weight']

const MUSCLE_SLUGS = [
  'chest', 'biceps', 'triceps', 'deltoids', 'abs', 'obliques',
  'quadriceps', 'hamstring', 'calves', 'gluteal',
  'trapezius', 'upper-back', 'lower-back', 'forearm', 'adductors', 'neck',
]

export default function CreateChallengeModal({ t, friends, onClose, onCreated }) {
  const [opponent, setOpponent] = useState('')
  const [type, setType] = useState('strength')
  const [deadline, setDeadline] = useState('')
  const [message, setMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')

  const [muscleGroup, setMuscleGroup] = useState('')
  const [enduranceMode, setEnduranceMode] = useState('treadmill')
  const [speed, setSpeed] = useState('')
  const [gradient, setGradient] = useState('')
  const [targetKg, setTargetKg] = useState('')

  const minDatetime = new Date(Date.now() + 60_000).toISOString().slice(0, 16)
  const needsDeadline = type !== 'target_weight'

  async function handleSend() {
    setError('')
    if (!opponent) { setError('Pick an opponent'); return }
    if (needsDeadline && !deadline) { setError('Set a deadline'); return }
    if (needsDeadline) {
      const dl = new Date(deadline)
      if (dl <= new Date()) { setError('Deadline must be in the future'); return }
    }

    if (type === 'strength' && !muscleGroup) { setError('Pick a muscle group'); return }
    if (type === 'endurance' && (!speed || parseFloat(speed) <= 0)) { setError('Set a speed'); return }
    if (type === 'target_weight' && (!targetKg || parseFloat(targetKg) <= 0)) { setError('Set a target weight'); return }

    const payload = {
      opponent_username: opponent,
      challenge_type: type,
      deadline: needsDeadline ? new Date(deadline).toISOString() : null,
      message: message.trim() || null,
    }

    if (type === 'strength') payload.muscle_group = muscleGroup
    if (type === 'endurance') {
      payload.endurance_mode = enduranceMode
      payload.endurance_speed = parseFloat(speed)
      if (enduranceMode === 'treadmill' && gradient) payload.endurance_gradient = parseFloat(gradient)
    }
    if (type === 'target_weight') payload.target_weight_kg = parseFloat(targetKg)

    setSending(true)
    try { await api.post('/challenges', payload); onCreated() }
    catch (err) { setError(err.response?.data?.detail || 'Error') }
    finally { setSending(false) }
  }

  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-card modal-card--wide" onClick={(e) => e.stopPropagation()} role="dialog">
        <h3 className="modal-title">{t.ch_send_title} ⚔️</h3>

        <label className="form-label">{t.ch_challenge} — {t.friends_title}</label>
        <select className="form-select" value={opponent} onChange={(e) => setOpponent(e.target.value)}>
          <option value="">—</option>
          {friends.map((f) => (
            <option key={f.id} value={f.username}>@{f.username} — {f.firstname} {f.lastname}</option>
          ))}
        </select>

        <label className="form-label">{t.ch_type}</label>
        <div className="challenge-type-picker">
          {TYPES.map((tp) => (
            <button key={tp} className={`challenge-type-btn ${type === tp ? 'active' : ''}`}
              onClick={() => setType(tp)}>
              {t[`ch_type_${tp}`]}
            </button>
          ))}
        </div>

        {type === 'strength' && (
          <>
            <label className="form-label">{t.ch_muscle_group}</label>
            <select className="form-select" value={muscleGroup} onChange={(e) => setMuscleGroup(e.target.value)}>
              <option value="">—</option>
              {MUSCLE_SLUGS.map((s) => (
                <option key={s} value={s}>{t[`muscle_${s.replace('-', '_')}`] || s}</option>
              ))}
            </select>
          </>
        )}

        {type === 'endurance' && (
          <>
            <label className="form-label">{t.ch_endurance_mode}</label>
            <div className="challenge-type-picker">
              {['treadmill', 'stairs'].map((m) => (
                <button key={m} className={`challenge-type-btn ${enduranceMode === m ? 'active' : ''}`}
                  onClick={() => setEnduranceMode(m)}>
                  {t[`ch_mode_${m}`]}
                </button>
              ))}
            </div>
            <label className="form-label">{t.ch_speed}</label>
            <input type="number" min="0" step="0.1" className="form-input"
              value={speed} onChange={(e) => setSpeed(e.target.value)} />
            {enduranceMode === 'treadmill' && (
              <>
                <label className="form-label">{t.ch_gradient}</label>
                <input type="number" min="0" step="0.5" className="form-input"
                  value={gradient} onChange={(e) => setGradient(e.target.value)} />
              </>
            )}
          </>
        )}

        {type === 'target_weight' && (
          <>
            <label className="form-label">{t.ch_target_kg}</label>
            <input type="number" min="0" step="0.1" className="form-input"
              value={targetKg} onChange={(e) => setTargetKg(e.target.value)} />
            <p className="muted" style={{ fontSize: 12, marginTop: 4 }}>{t.ch_first_wins}</p>
          </>
        )}

        {needsDeadline && (
          <>
            <label className="form-label">{t.ch_deadline}</label>
            <input type="datetime-local" className="form-input" value={deadline}
              min={minDatetime} onChange={(e) => setDeadline(e.target.value)} />
          </>
        )}

        <label className="form-label">{t.ch_message}</label>
        <textarea className="form-textarea" rows={2} value={message}
          onChange={(e) => setMessage(e.target.value)} placeholder={t.ch_message_ph} />

        {error && <p className="tiny-msg err">{error}</p>}

        <div className="modal-actions">
          <button className="btn btn-secondary" onClick={onClose} disabled={sending}>{t.ch_cancel}</button>
          <button className="btn btn-primary" onClick={handleSend} disabled={sending}>
            {sending ? '…' : t.ch_send}
          </button>
        </div>
      </div>
    </div>
  )
}
