import { useState, useEffect, useMemo, useCallback } from 'react'
import { useApp } from '../contexts/AppContext'
import api from '../api/client'
import { translations } from '../i18n'
import WorkoutCard from '../components/workouts/WorkoutCard'
import WorkoutDetail from '../components/workouts/WorkoutDetail'
import AddPlanToProfileModal from '../components/workouts/AddPlanToProfileModal'
import AddWorkoutPlanModal from '../components/workouts/AddWorkoutPlanModal'

const FREQUENCY_OPTIONS = [
  { value: 'all', label_key: 'workouts_freq_all', fallback: 'All' },
  { value: 3, label_key: 'workouts_freq_3', fallback: '3× / week' },
  { value: 4, label_key: 'workouts_freq_4', fallback: '4× / week' },
  { value: 5, label_key: 'workouts_freq_5', fallback: '5× / week' },
]

export default function Workouts() {
  const { t, lang } = useApp()
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [frequency, setFrequency] = useState('all')
  const [selectedPlan, setSelectedPlan] = useState(null)
  const [activePlan, setActivePlan] = useState(null)
  const [planForLifts, setPlanForLifts] = useState(null)
  const [detailLang, setDetailLang] = useState(null)
  const [showCreate, setShowCreate] = useState(false)

  const loadPlans = useCallback(() => {
    setLoading(true)
    const params = { limit: 100 }
    if (frequency !== 'all') params.days_per_week = frequency
    return api.get('/workouts', { params })
      .then(r => setPlans(r.data))
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [frequency])

  useEffect(() => { loadPlans() }, [loadPlans])

  useEffect(() => {
    api.get('/me/workout-plan')
      .then(r => setActivePlan(r.data))
      .catch(() => setActivePlan(null))
  }, [])

  const initialLiftsForCurrent = useMemo(() => {
    if (!planForLifts || !activePlan || activePlan.plan?.id !== planForLifts.id) return {}
    return (activePlan.lifts || []).reduce((acc, l) => {
      acc[l.exercise_name] = l.weight_kg
      return acc
    }, {})
  }, [planForLifts, activePlan])

  const handleView = async (plan) => {
    try {
      const r = await api.post(`/workouts/${plan.id}/view`)
      setSelectedPlan(r.data)
      setPlans(prev => prev.map(p => p.id === plan.id
        ? { ...p, views: r.data.views }
        : p))
    } catch {
      try {
        const r = await api.get(`/workouts/${plan.id}`)
        setSelectedPlan(r.data)
      } catch { /* ignore */ }
    }
  }

  const handleRate = async (planId, score) => {
    try {
      const r = await api.post(`/workouts/${planId}/rate`, { score })
      setPlans(prev => prev.map(p => p.id === planId
        ? { ...p, rating: r.data.rating, rating_count: r.data.rating_count }
        : p))
      if (selectedPlan?.id === planId) setSelectedPlan(r.data)
    } catch { /* ignore */ }
  }

  const sections = useMemo(() => {
    if (frequency !== 'all') return null
    const byDays = new Map()
    for (const p of plans) {
      const key = p.days_per_week
      if (!byDays.has(key)) byDays.set(key, [])
      byDays.get(key).push(p)
    }
    return [...byDays.keys()]
      .sort((a, b) => a - b)
      .map((days) => ({ days, plans: byDays.get(days) }))
  }, [plans, frequency])

  return (
    <div className="workouts-page">
      <div className="workouts-top">
        <div>
          <h1 className="workouts-title">{t.workouts_title || 'Workout Plans'} 🏋️</h1>
          <p className="workouts-subtitle">
            {t.workouts_sub || 'Science-based training plans tailored to how often you can train.'}
          </p>
        </div>
        <button
          className="btn btn-primary workouts-create-btn"
          onClick={() => setShowCreate(true)}
        >
          ➕ {t.workouts_create_btn || 'Add Workout Plan'}
        </button>
      </div>

      <div className="workouts-toolbar">
        <div className="workouts-freq-label">
          {t.workouts_freq_prompt || 'How many days per week?'}
        </div>
        <div className="filter-tabs">
          {FREQUENCY_OPTIONS.map(opt => (
            <button
              key={opt.value}
              className={`filter-tab${frequency === opt.value ? ' active' : ''}`}
              onClick={() => setFrequency(opt.value)}
            >
              {t[opt.label_key] || opt.fallback}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="meals-loading">{t.admin_loading || 'Loading…'}</div>
      ) : plans.length === 0 ? (
        <div className="empty-card">{t.workouts_empty || 'No workout plans found.'}</div>
      ) : sections ? (
        <>
          {sections.map(s => (
            <section className="meals-section" key={s.days}>
              <div className="meals-carousel-header">
                <div>
                  <h2 className="meals-section-title">
                    {s.days}-{t.workouts_day_split || 'Day Split'}
                  </h2>
                  <p className="meals-section-sub">
                    {t[`workouts_section_${s.days}day_sub`] || `${s.days} sessions per week`}
                  </p>
                </div>
              </div>
              <div
                className="workouts-section-grid"
                style={{ gridTemplateColumns: `repeat(${Math.min(s.plans.length, 3)}, minmax(0, 1fr))` }}
              >
                {s.plans.map(p => (
                  <WorkoutCard key={p.id} plan={p} t={t} onView={handleView} appLang={lang} />
                ))}
              </div>
            </section>
          ))}
        </>
      ) : (
        <section className="meals-section">
          <div className="meals-carousel-header">
            <div>
              <h2 className="meals-section-title">
                {frequency}-{t.workouts_day_split || 'Day Split'}
              </h2>
              {t[`workouts_section_${frequency}day_sub`] && (
                <p className="meals-section-sub">{t[`workouts_section_${frequency}day_sub`]}</p>
              )}
            </div>
          </div>
          <div className="workouts-vertical-grid">
            {plans.map(p => (
              <WorkoutCard key={p.id} plan={p} t={t} onView={handleView} appLang={lang} />
            ))}
          </div>
        </section>
      )}

      {selectedPlan && (
        <WorkoutDetail
          plan={selectedPlan}
          t={t}
          appLang={lang}
          onClose={() => setSelectedPlan(null)}
          onRate={handleRate}
          onAddToProfile={(p, modalLang) => { setPlanForLifts(p); setDetailLang(modalLang || lang) }}
          isActive={activePlan?.plan?.id === selectedPlan.id}
        />
      )}

      {planForLifts && (
        <AddPlanToProfileModal
          plan={planForLifts}
          t={translations[detailLang || lang] || t}
          appLang={detailLang || lang}
          initialLifts={initialLiftsForCurrent}
          mode={activePlan?.plan?.id === planForLifts.id ? 'update' : 'add'}
          onClose={() => setPlanForLifts(null)}
          onSaved={(data) => { setActivePlan(data); setPlanForLifts(null) }}
        />
      )}

      {showCreate && (
        <AddWorkoutPlanModal
          t={t}
          appLang={lang}
          onClose={() => setShowCreate(false)}
          onCreated={() => {
            setShowCreate(false)
            setFrequency('all')
            setLoading(true)
            api.get('/workouts', { params: { limit: 100 } })
              .then(r => setPlans(r.data))
              .catch(() => {})
              .finally(() => setLoading(false))
          }}
        />
      )}
    </div>
  )
}
