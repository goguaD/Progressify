import { useState } from 'react'
import api from '../api/client'

const REASONS_MEAL = [
  'report_reason_spam',
  'report_reason_inappropriate',
  'report_reason_incorrect',
  'report_reason_copied',
  'report_reason_other',
]

const REASONS_WORKOUT = [
  'report_reason_spam',
  'report_reason_inappropriate',
  'report_reason_dangerous',
  'report_reason_incorrect',
  'report_reason_copied',
  'report_reason_other',
]

export default function ReportModal({ targetType, targetId, targetName, t, onClose }) {
  const reasons = targetType === 'meal' ? REASONS_MEAL : REASONS_WORKOUT
  const [reason, setReason] = useState('')
  const [notes, setNotes] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [done, setDone] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    if (!reason) return
    setSubmitting(true)
    try {
      const endpoint = targetType === 'meal'
        ? `/meals/${targetId}/report`
        : `/workouts/${targetId}/report`
      await api.post(endpoint, { reason: t[reason] || reason, notes: notes.trim() || null })
      setDone(true)
    } catch {
      /* silently fail */
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="report-modal" onClick={(e) => e.stopPropagation()}>
        <div className="report-modal-header">
          <h2 className="report-modal-title">🚩 {t.report_title}</h2>
          <button className="report-modal-close" onClick={onClose}>✕</button>
        </div>

        {done ? (
          <div className="report-success">
            <span className="report-success-icon">✅</span>
            <p>{t.report_success}</p>
            <button className="btn btn-secondary" onClick={onClose} style={{ marginTop: 16 }}>
              {t.report_cancel}
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <p className="report-subtitle">{t.report_subtitle}</p>
            <p className="report-target-name">
              {targetType === 'meal' ? '🥗' : '🏋️'} <strong>{targetName}</strong>
            </p>

            <div className="report-reasons">
              {reasons.map((key) => (
                <label key={key} className={`report-reason-option${reason === key ? ' selected' : ''}`}>
                  <input
                    type="radio"
                    name="reason"
                    value={key}
                    checked={reason === key}
                    onChange={() => setReason(key)}
                  />
                  {t[key] || key}
                </label>
              ))}
            </div>

            <div className="report-notes-wrap">
              <label className="form-label">{t.report_notes_label}</label>
              <textarea
                className="form-input"
                rows={3}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                placeholder="..."
              />
            </div>

            <div className="report-modal-footer">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={onClose}
              >
                {t.report_cancel}
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={!reason || submitting}
              >
                {submitting ? '…' : t.report_submit}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  )
}
