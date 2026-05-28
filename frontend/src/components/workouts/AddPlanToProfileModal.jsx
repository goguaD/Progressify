import { useEffect, useMemo, useState } from 'react'
import api from '../../api/client'

function uniqueExercises(plan) {
  const seen = new Set()
  const out = []
  for (const day of plan?.days || []) {
    for (const ex of day.exercises || []) {
      if (seen.has(ex.name)) continue
      seen.add(ex.name)
      out.push(ex)
    }
  }
  return out
}

function hintFor(ex, appLang) {
  if (appLang === 'ka' && ex.unit_hint_ka) return ex.unit_hint_ka
  return ex.unit_hint || null
}

export default function AddPlanToProfileModal({
  plan,
  t,
  appLang = 'en',
  initialLifts = {},
  initialHints = {},
  mode = 'add',
  onClose,
  onSaved,
}) {
  const exercises = useMemo(() => uniqueExercises(plan), [plan])
  const [values, setValues] = useState(() => {
    const init = {}
    for (const ex of uniqueExercises(plan)) {
      init[ex.name] = initialLifts[ex.name] != null ? String(initialLifts[ex.name]) : ''
    }
    return init
  })
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    const init = {}
    for (const ex of exercises) {
      init[ex.name] = initialLifts[ex.name] != null ? String(initialLifts[ex.name]) : ''
    }
    setValues(init)
  }, [plan?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!plan) return null

  const handleChange = (name, raw) => {
    if (raw === '' || /^[0-9]*\.?[0-9]*$/.test(raw)) {
      setValues((v) => ({ ...v, [name]: raw }))
    }
  }

  const handleSubmit = async () => {
    setError('')
    const lifts = exercises.map((ex) => {
      const raw = values[ex.name] ?? ''
      const num = raw === '' ? 0 : Number.parseFloat(raw)
      return { exercise_name: ex.name, weight_kg: Number.isFinite(num) ? num : 0 }
    })
    setSaving(true)
    try {
      let data
      if (mode === 'update') {
        const r = await api.patch('/me/workout-plan/lifts', { lifts })
        data = r.data
      } else {
        const r = await api.post('/me/workout-plan', { plan_id: plan.id, lifts })
        data = r.data
      }
      onSaved?.(data)
      onClose?.()
    } catch (err) {
      setError(err.response?.data?.detail || 'Could not save your plan.')
    } finally {
      setSaving(false)
    }
  }

  const title = mode === 'update'
    ? (t.profile_update_lifts_title || 'Update your one-rep maxes')
    : (t.profile_add_plan_title || 'Add this plan to your profile')

  const subtitle = mode === 'update'
    ? (t.profile_update_lifts_sub
       || 'Adjust any lift that has improved. Empty fields stay at zero.')
    : (t.profile_add_plan_sub
       || 'Enter the heaviest weight you can lift for one clean repetition (your 1RM) for each exercise. Leave a field blank if you have not tested that lift.')

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="add-plan-modal" onClick={(e) => e.stopPropagation()}>
        <button className="meal-detail-close" onClick={onClose} aria-label="Close">✕</button>

        <h2 className="add-plan-modal-title">{title}</h2>
        <p className="add-plan-modal-sub">{subtitle}</p>

        <div className="add-plan-plan-card">
          <div className="add-plan-plan-name">
            {appLang === 'ka' && plan.name_ka ? plan.name_ka : plan.name}
          </div>
          <div className="add-plan-plan-meta">
            <span>{plan.days_per_week}× / {t.workouts_week || 'week'}</span>
            <span>·</span>
            <span>{t[`workouts_level_${plan.level}`] || plan.level}</span>
          </div>
        </div>

        <div className="add-plan-lifts-list">
          {exercises.map((ex) => {
            const exName = appLang === 'ka' && ex.name_ka ? ex.name_ka : ex.name
            const inlineHint = hintFor(ex, appLang) || initialHints[ex.name]
            return (
              <div key={ex.name} className="add-plan-lift-block">
                <div className="add-plan-lift-row">
                  <div className="add-plan-lift-info">
                    <div className="add-plan-lift-name">{exName}</div>
                    <div className="add-plan-lift-muscle">
                      {t[`workouts_muscle_${ex.muscle_group}`] || ex.muscle_group}
                    </div>
                  </div>
                  <div className="add-plan-lift-input-wrap">
                    <input
                      type="text"
                      inputMode="decimal"
                      className="add-plan-lift-input"
                      placeholder="0"
                      value={values[ex.name] ?? ''}
                      onChange={(e) => handleChange(ex.name, e.target.value)}
                    />
                    <span className="add-plan-lift-unit">kg</span>
                  </div>
                </div>
                {inlineHint && (
                  <p className="add-plan-lift-hint">
                    <span className="add-plan-lift-hint-icon">ℹ️</span>
                    {inlineHint}
                  </p>
                )}
              </div>
            )
          })}
        </div>

        {error && <p className="tiny-msg err" style={{ marginTop: 12 }}>{error}</p>}

        <div className="add-plan-actions">
          <button className="btn btn-secondary" onClick={onClose} disabled={saving}>
            {t.profile_cancel || 'Cancel'}
          </button>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={saving}>
            {saving
              ? (t.profile_saving || 'Saving…')
              : (mode === 'update'
                  ? (t.profile_save_lifts || 'Save changes')
                  : (t.profile_add_plan_save || 'Save plan to profile'))}
          </button>
        </div>
      </div>
    </div>
  )
}
