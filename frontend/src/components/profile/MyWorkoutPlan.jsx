import { useEffect, useState } from 'react'
import api, { resolveAssetUrl } from '../../api/client'

export default function MyWorkoutPlan({
  plan,
  t,
  appLang = 'en',
  editable = false,
  onChange,
  onUpdate,
  onRemove,
}) {
  const [days, setDays] = useState(null)
  const [loading, setLoading] = useState(false)
  const [activeDay, setActiveDay] = useState(0)

  // The profile summary endpoint returns a plan summary (no days). When this
  // component is rendered for the active user we fetch the full plan once so
  // the lifter can review the schedule below the muscle map.
  useEffect(() => {
    if (!plan?.id) {
      setDays(null)
      return
    }
    if (Array.isArray(plan.days) && plan.days.length > 0) {
      setDays(plan.days)
      return
    }
    setLoading(true)
    api.get(`/workouts/${plan.id}`)
      .then((r) => setDays(r.data.days || []))
      .catch(() => setDays([]))
      .finally(() => setLoading(false))
  }, [plan?.id, plan?.days])

  if (!plan) {
    if (!editable) return null
    return (
      <section className="my-plan-card my-plan-empty">
        <div>
          <h2 className="anatomy-title">{t.profile_my_plan_title || 'My workout plan'} 📋</h2>
          <p className="anatomy-sub">
            {t.profile_my_plan_empty
             || 'You have not chosen a workout programme yet. Pick one from the Workouts page to populate your anatomy chart.'}
          </p>
        </div>
        {onChange && (
          <button className="btn btn-primary" onClick={onChange}>
            {t.profile_my_plan_choose || 'Browse workout plans'}
          </button>
        )}
      </section>
    )
  }

  const planName = appLang === 'ka' && plan.name_ka ? plan.name_ka : plan.name
  const planDesc = appLang === 'ka' && plan.description_ka ? plan.description_ka : plan.description
  const day = Array.isArray(days) ? days[activeDay] : null
  const dayName = day && appLang === 'ka' && day.name_ka ? day.name_ka : day?.name

  return (
    <section className="my-plan-card">
      <div className="my-plan-head">
        <div className="my-plan-head-info">
          <h2 className="anatomy-title">{t.profile_my_plan_title || 'My workout plan'} 📋</h2>
          <p className="anatomy-sub">
            {t.profile_my_plan_sub
             || 'The training programme currently driving your strength and muscle development.'}
          </p>
        </div>
        {editable && (
          <div className="my-plan-actions">
            {onUpdate && (
              <button className="btn btn-secondary" onClick={onUpdate}>
                {t.profile_orm_update || 'Update lifts'}
              </button>
            )}
            {onChange && (
              <button className="btn btn-secondary" onClick={onChange}>
                {t.profile_my_plan_change || 'Change plan'}
              </button>
            )}
            {onRemove && (
              <button className="btn btn-secondary" onClick={onRemove}>
                {t.profile_my_plan_remove || 'Remove'}
              </button>
            )}
          </div>
        )}
      </div>

      <div className="my-plan-body">
        {plan.image_url && (
          <div
            className="my-plan-cover"
            style={{ backgroundImage: `url(${resolveAssetUrl(plan.image_url)})` }}
          />
        )}
        <div className="my-plan-info">
          <h3 className="my-plan-name">{planName}</h3>
          <div className="my-plan-meta">
            <span className="chip">{plan.days_per_week}× / {t.workouts_week || 'week'}</span>
            <span className="chip">{t[`workouts_level_${plan.level}`] || plan.level}</span>
            {plan.split_type && (
              <span className="chip">
                {t[`workouts_split_${plan.split_type}`] || plan.split_type.replace(/_/g, ' ')}
              </span>
            )}
          </div>
          {planDesc && <p className="my-plan-desc">{planDesc}</p>}
        </div>
      </div>

      {loading && <p className="muted" style={{ marginTop: 12 }}>{t.admin_loading || 'Loading…'}</p>}

      {Array.isArray(days) && days.length > 0 && (
        <div className="my-plan-days">
          <div className="my-plan-day-tabs">
            {days.map((d, i) => {
              const dn = appLang === 'ka' && d.name_ka ? d.name_ka : d.name
              return (
                <button
                  key={d.id}
                  className={`workout-day-tab${i === activeDay ? ' active' : ''}`}
                  onClick={() => setActiveDay(i)}
                >
                  <span className="workout-day-tab-num">{t.workouts_day || 'Day'} {d.day_number}</span>
                  <span className="workout-day-tab-name">{dn}</span>
                </button>
              )
            })}
          </div>

          {day && (
            <div className="my-plan-day-detail">
              <div className="my-plan-day-header">
                <h4 className="my-plan-day-title">{dayName}</h4>
                {day.focus && <span className="workout-day-focus">{day.focus}</span>}
              </div>
              <div className="my-plan-exercise-grid">
                {day.exercises.map((ex) => {
                  const exName = appLang === 'ka' && ex.name_ka ? ex.name_ka : ex.name
                  const repRange = ex.rep_low === ex.rep_high
                    ? `${ex.rep_low}`
                    : `${ex.rep_low}–${ex.rep_high}`
                  return (
                    <div key={ex.id} className="my-plan-exercise">
                      <div className="my-plan-exercise-name">{exName}</div>
                      <div className="my-plan-exercise-meta">
                        <span>{ex.sets} × {repRange}</span>
                        <span>·</span>
                        <span>
                          {ex.rest_seconds >= 60
                            ? `${Math.round(ex.rest_seconds / 60)}m ${t.workouts_rest || 'rest'}`
                            : `${ex.rest_seconds}s ${t.workouts_rest || 'rest'}`}
                        </span>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
