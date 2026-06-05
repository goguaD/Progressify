import { useState, useEffect } from 'react'
import StarRating from '../meals/StarRating'
import ExerciseMuscleMap from './ExerciseMuscleMap'
import { musclesForExercise } from './exerciseMuscles'
import { resolveAssetUrl } from '../../api/client'
import { translations } from '../../i18n'

const PURPOSE_META = {
  strength: { en: 'Strength', ka: 'ძალა', cls: 'strength', emoji: '🏋️' },
  hypertrophy: { en: 'Hypertrophy', ka: 'ჰიპერტროფია', cls: 'hypertrophy', emoji: '💪' },
  endurance: { en: 'Endurance', ka: 'ენდურანსი', cls: 'endurance', emoji: '🔄' },
}

function readUserGender() {
  try {
    const u = JSON.parse(localStorage.getItem('user') || 'null')
    return u?.gender === 'female' ? 'female' : 'male'
  } catch { return 'male' }
}

export default function WorkoutDetail({
  plan, t, onClose, onRate, onAddToProfile,
  isActive = false,
  appLang: appLangProp,
}) {
  const [appLang, setAppLang] = useState(appLangProp || 'en')
  const [activeDay, setActiveDay] = useState(0)
  const gender = readUserGender()

  // Keep content language in sync when the app-level language changes
  useEffect(() => {
    if (appLangProp) setAppLang(appLangProp)
  }, [appLangProp])

  // Use translations that match the modal's own language toggle
  const localT = translations[appLang] || t

  if (!plan) return null

  const name = appLang === 'ka' && plan.name_ka ? plan.name_ka : plan.name
  const description = appLang === 'ka' && plan.description_ka ? plan.description_ka : plan.description

  const day = plan.days?.[activeDay]
  const dayName = day && appLang === 'ka' && day.name_ka ? day.name_ka : day?.name

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="workout-detail-modal" onClick={e => e.stopPropagation()}>
        <button className="meal-detail-close" onClick={onClose} aria-label="Close">✕</button>

        <div
          className="workout-detail-hero"
          style={{ backgroundImage: plan.image_url ? `url(${resolveAssetUrl(plan.image_url)})` : undefined }}
        >
          <div className="workout-detail-hero-overlay">
            <div className="workout-detail-lang-switch">
              <button
                className={`lang-pill${appLang === 'en' ? ' active' : ''}`}
                onClick={() => setAppLang('en')}
              >EN</button>
              <button
                className={`lang-pill${appLang === 'ka' ? ' active' : ''}`}
                onClick={() => setAppLang('ka')}
              >ქა</button>
            </div>
            <h2 className="workout-detail-name">{name}</h2>
            <div className="workout-detail-meta">
              <span className="workout-meta-pill">
                📅 {plan.days_per_week}× / {localT.workouts_week || 'week'}
              </span>
              <span className="workout-meta-pill">
                🎯 {localT[`workouts_level_${plan.level}`] || plan.level}
              </span>
              <span className="workout-meta-pill">
                🧠 {localT[`workouts_split_${plan.split_type}`] || plan.split_type.replace(/_/g, ' ')}
              </span>
            </div>
          </div>
        </div>

        <div className="workout-detail-body">
          <p className="workout-detail-desc">{description}</p>

          {/* Rating section */}
          <div className="workout-detail-rating-row">
            <div className="workout-detail-avg-rating">
              <StarRating rating={plan.rating} size={20} />
              <span className="workout-detail-rating-text">
                {plan.rating.toFixed(1)} ({plan.rating_count})
              </span>
            </div>
            {onRate && (
              <div className="workout-detail-my-rating">
                <span className="workout-detail-my-label">
                  {localT.workouts_your_rating || 'Your rating:'}
                </span>
                <StarRating
                  rating={plan.my_rating || 0}
                  size={22}
                  interactive
                  onRate={(score) => onRate(plan.id, score)}
                />
              </div>
            )}
          </div>

          {onAddToProfile && (
            <div className="workout-detail-add-row">
              <button
                className="btn btn-primary workout-detail-add-btn"
                onClick={() => onAddToProfile(plan, appLang)}
              >
                {isActive
                  ? (localT.workouts_replace_active || '🔁 Replace active plan')
                  : (localT.workouts_add_to_profile || '➕ Add this plan to my profile')}
              </button>
              {isActive && (
                <span className="workout-detail-active-flag">
                  {localT.workouts_active_plan || '✓ Currently active'}
                </span>
              )}
            </div>
          )}

          <RepRangeLegend t={localT} appLang={appLang} />

          <div className="workout-detail-day-tabs">
            {plan.days.map((d, i) => {
              const dn = appLang === 'ka' && d.name_ka ? d.name_ka : d.name
              return (
                <button
                  key={d.id}
                  className={`workout-day-tab${i === activeDay ? ' active' : ''}`}
                  onClick={() => setActiveDay(i)}
                >
                  <span className="workout-day-tab-num">{localT.workouts_day || 'Day'} {d.day_number}</span>
                  <span className="workout-day-tab-name">{dn}</span>
                </button>
              )
            })}
          </div>

          {day && (
            <div className="workout-day-content">
              <div className="workout-day-header">
                <h3 className="workout-day-title">{dayName}</h3>
                {day.focus && <span className="workout-day-focus">{day.focus}</span>}
              </div>

              <div className="workout-exercises">
                {day.exercises.map(ex => (
                  <ExerciseCard key={ex.id} ex={ex} t={localT} appLang={appLang} gender={gender} />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}


function ExerciseCard({ ex, t, appLang, gender }) {
  const [expanded, setExpanded] = useState(false)
  const name = appLang === 'ka' && ex.name_ka ? ex.name_ka : ex.name
  const description = appLang === 'ka' && ex.description_ka ? ex.description_ka : ex.description
  const purpose = PURPOSE_META[ex.primary_purpose] || PURPOSE_META.hypertrophy
  const purposeLabel = appLang === 'ka' ? purpose.ka : purpose.en

  const hasTargets = Array.isArray(ex.muscle_targets) && ex.muscle_targets.length > 0
  const { primary, secondary } = hasTargets
    ? { primary: [], secondary: [] }
    : musclesForExercise(ex)

  const repRange = ex.rep_low === ex.rep_high ? `${ex.rep_low}` : `${ex.rep_low}–${ex.rep_high}`

  return (
    <div className="exercise-card">
      <ExerciseMuscleMap
        primary={primary}
        secondary={secondary}
        targets={hasTargets ? ex.muscle_targets : null}
        gender={gender}
      />
      <div className="exercise-card-body">
        <div className="exercise-card-header">
          <h4 className="exercise-card-name">{name}</h4>
          <span className={`exercise-purpose-pill ${purpose.cls}`}>
            {purpose.emoji} {purposeLabel}
          </span>
        </div>

        <div className="exercise-stats">
          <div className="exercise-stat">
            <div className="exercise-stat-label">{t.workouts_sets || 'Sets'}</div>
            <div className="exercise-stat-value">{ex.sets}</div>
          </div>
          <div className="exercise-stat">
            <div className="exercise-stat-label">{t.workouts_reps || 'Reps'}</div>
            <div className="exercise-stat-value">{repRange}</div>
          </div>
          <div className="exercise-stat">
            <div className="exercise-stat-label">{t.workouts_rest || 'Rest'}</div>
            <div className="exercise-stat-value">
              {ex.rest_seconds >= 60 ? `${Math.round(ex.rest_seconds / 60)}m` : `${ex.rest_seconds}s`}
            </div>
          </div>
        </div>

        <ExerciseMuscleLegend t={t} appLang={appLang} />

        <p className={`exercise-card-desc${expanded ? ' expanded' : ''}`}>
          {description}
        </p>
        {description && description.length > 140 && (
          <button className="exercise-toggle" onClick={() => setExpanded(v => !v)}>
            {expanded ? (t.workouts_show_less || 'Show less') : (t.workouts_show_more || 'Show more')}
          </button>
        )}
      </div>
    </div>
  )
}


function ExerciseMuscleLegend({ t, appLang }) {
  return (
    <div className="exercise-muscle-legend">
      <div className="exercise-muscle-legend-item">
        <span className="exercise-muscle-dot primary" />
        <span>{appLang === 'ka' ? 'მთავარი' : (t.workouts_primary_muscle || 'Primary')}</span>
      </div>
      <div className="exercise-muscle-legend-item">
        <span className="exercise-muscle-dot secondary" />
        <span>{appLang === 'ka' ? 'დამხმარე' : (t.workouts_secondary_muscle || 'Secondary')}</span>
      </div>
    </div>
  )
}


function RepRangeLegend({ t, appLang }) {
  const items = [
    { range: '1–5', purpose: 'strength', emoji: '🏋️', en: 'Strength', ka: 'ძალა',
      en_desc: 'Heavy weight (≥85% 1RM), long rest. Builds maximal force.',
      ka_desc: 'მძიმე წონები (≥85% 1RM), გრძელი დასვენება. ვითარდება მაქსიმალური ძალა.' },
    { range: '6–12', purpose: 'hypertrophy', emoji: '💪', en: 'Hypertrophy', ka: 'ჰიპერტროფია',
      en_desc: 'Moderate weight (~70-85% 1RM), 1-2 min rest. Best for muscle growth.',
      ka_desc: 'საშუალო წონები (~70-85% 1RM), 1-2 წთ დასვენება. საუკეთესოა კუნთის ზრდისთვის.' },
    { range: '13+', purpose: 'endurance', emoji: '🔄', en: 'Endurance', ka: 'ენდურანსი',
      en_desc: 'Lighter weight (<67% 1RM), short rest. Builds muscular stamina.',
      ka_desc: 'მსუბუქი წონები (<67% 1RM), მოკლე დასვენება. ვითარდება გამძლეობა.' },
  ]
  return (
    <div className="rep-range-legend">
      <div className="rep-range-legend-title">
        🧠 {t.workouts_rep_guide || 'Rep range guide'}
      </div>
      <div className="rep-range-legend-items">
        {items.map(i => (
          <div key={i.purpose} className={`rep-range-item ${i.purpose}`}>
            <div className="rep-range-item-head">
              <span className="rep-range-emoji">{i.emoji}</span>
              <span className="rep-range-num">{i.range} reps</span>
            </div>
            <div className="rep-range-label">{appLang === 'ka' ? i.ka : i.en}</div>
            <div className="rep-range-desc">{appLang === 'ka' ? i.ka_desc : i.en_desc}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
