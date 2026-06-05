import { useEffect } from 'react'

export default function ConfirmUnfriendModal({ t, target, busy, onCancel, onConfirm }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape' && !busy) onCancel() }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [busy, onCancel])

  const text = t.confirm_unfriend_text.replace('{username}', target.username)

  return (
    <div className="modal-backdrop" onClick={onCancel}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <h3 className="modal-title">{t.confirm_unfriend_title}</h3>
        <p className="modal-text">{text}</p>
        <div className="modal-actions">
          <button className="btn btn-secondary" disabled={busy} onClick={onCancel}>
            {t.confirm_no}
          </button>
          <button className="btn btn-danger" disabled={busy} onClick={onConfirm} autoFocus>
            {busy ? '…' : t.confirm_yes}
          </button>
        </div>
      </div>
    </div>
  )
}
