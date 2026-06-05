export default function DeadlinePopup({ alert, t, onClose }) {
  if (!alert) return null
  return (
    <div className="deadline-popup">
      <span>⚠️ {t.ch_deadline_soon} — <b>{t[`ch_type_${alert.challenge_type}`]}</b></span>
      <button className="deadline-popup-close" onClick={onClose}>✕</button>
    </div>
  )
}
