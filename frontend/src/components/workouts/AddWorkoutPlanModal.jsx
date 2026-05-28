import { useEffect, useMemo, useState } from 'react'
import api from '../../api/client'
import ExerciseMuscleMap from './ExerciseMuscleMap'

const LANG_OPTIONS = [
  { value: 'en',   labelKey: 'meals_lang_en' },
  { value: 'ka',   labelKey: 'meals_lang_ka' },
  { value: 'both', labelKey: 'meals_lang_both' },
]

const LEVEL_OPTIONS = [
  { value: 'beginner',     labelKey: 'workouts_level_beginner',     fallback: 'Beginner' },
  { value: 'intermediate', labelKey: 'workouts_level_intermediate', fallback: 'Intermediate' },
  { value: 'advanced',     labelKey: 'workouts_level_advanced',     fallback: 'Advanced' },
]

const PURPOSE_OPTIONS = [
  { value: 'strength',    en: 'Strength',    ka: 'ძალა',           emoji: '🏋️' },
  { value: 'hypertrophy', en: 'Hypertrophy', ka: 'ჰიპერტროფია',     emoji: '💪' },
  { value: 'endurance',   en: 'Endurance',   ka: 'გამძლეობა',       emoji: '🔄' },
]

const INTENSITY_OPTIONS = [
  { value: 'low',    en: 'Low',    ka: 'დაბალი' },
  { value: 'medium', en: 'Medium', ka: 'საშუალო' },
  { value: 'high',   en: 'High',   ka: 'მაღალი' },
]

// Slugs compatible with react-muscle-highlighter / BodyFigure.
const MUSCLE_SLUGS = [
  { slug: 'chest',       en: 'Chest',           ka: 'მკერდი' },
  { slug: 'upper-back',  en: 'Upper Back',      ka: 'ზედა ზურგი' },
  { slug: 'lower-back',  en: 'Lower Back',      ka: 'ქვედა ზურგი' },
  { slug: 'trapezius',   en: 'Trapezius',       ka: 'ტრაპეცია' },
  { slug: 'deltoids',    en: 'Shoulders',       ka: 'მხრები' },
  { slug: 'biceps',      en: 'Biceps',          ka: 'ბიცეფსი' },
  { slug: 'triceps',     en: 'Triceps',         ka: 'ტრიცეფსი' },
  { slug: 'forearm',     en: 'Forearms',        ka: 'წინამხარი' },
  { slug: 'abs',         en: 'Abs',             ka: 'მუცელი' },
  { slug: 'obliques',    en: 'Obliques',        ka: 'ირიბი მუცელი' },
  { slug: 'quadriceps',  en: 'Quadriceps',      ka: 'კვადრიცეფსი' },
  { slug: 'hamstring',   en: 'Hamstrings',      ka: 'ბარძაყის უკანა' },
  { slug: 'gluteal',     en: 'Glutes',          ka: 'დუნდულო' },
  { slug: 'calves',      en: 'Calves',          ka: 'წვივი' },
  { slug: 'adductors',   en: 'Adductors',       ka: 'მომზიდველი' },
  { slug: 'neck',        en: 'Neck',            ka: 'კისერი' },
]

const MUSCLE_GROUP_OPTIONS = [
  'chest', 'back', 'shoulders', 'biceps', 'triceps',
  'quadriceps', 'hamstring', 'calves', 'abs', 'glutes', 'general',
]

function purposeFromReps(low, high) {
  const mid = (Number(low) + Number(high)) / 2
  if (mid <= 5) return 'strength'
  if (mid <= 12) return 'hypertrophy'
  return 'endurance'
}

function newExercise() {
  return {
    name: '', name_ka: '',
    description: '', description_ka: '',
    sets: 3, rep_low: 8, rep_high: 12, rest_seconds: 90,
    primary_purpose: 'hypertrophy',
    muscle_group: 'general',
    targets: [],
  }
}

function newDay(num) {
  return {
    day_number: num,
    name: `Day ${num}`,
    name_ka: '',
    focus: '',
    exercises: [newExercise()],
  }
}

export default function AddWorkoutPlanModal({ t, appLang = 'en', onClose, onCreated }) {
  const [langChoice, setLangChoice] = useState('en')
  const [name, setName] = useState('')
  const [nameKa, setNameKa] = useState('')
  const [description, setDescription] = useState('')
  const [descriptionKa, setDescriptionKa] = useState('')
  const [daysPerWeek, setDaysPerWeek] = useState(3)
  const [splitType, setSplitType] = useState('')
  const [level, setLevel] = useState('intermediate')
  const [days, setDays] = useState(() => [newDay(1), newDay(2), newDay(3)])
  const [image, setImage] = useState(null)
  const [preview, setPreview] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const showEn = langChoice === 'en' || langChoice === 'both'
  const showKa = langChoice === 'ka' || langChoice === 'both'

  // Keep day count in sync with daysPerWeek.
  useEffect(() => {
    setDays((prev) => {
      if (prev.length === daysPerWeek) return prev
      if (prev.length < daysPerWeek) {
        const extra = []
        for (let i = prev.length; i < daysPerWeek; i++) {
          extra.push(newDay(i + 1))
        }
        return [...prev, ...extra]
      }
      return prev.slice(0, daysPerWeek).map((d, i) => ({ ...d, day_number: i + 1 }))
    })
  }, [daysPerWeek])

  const handleImage = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setImage(file)
    setPreview(URL.createObjectURL(file))
  }

  const updateDay = (idx, patch) => {
    setDays((prev) => prev.map((d, i) => (i === idx ? { ...d, ...patch } : d)))
  }
  const updateExercise = (dIdx, eIdx, patch) => {
    setDays((prev) => prev.map((d, i) => {
      if (i !== dIdx) return d
      const exercises = d.exercises.map((ex, j) => (j === eIdx ? { ...ex, ...patch } : ex))
      return { ...d, exercises }
    }))
  }
  const addExercise = (dIdx) => {
    setDays((prev) => prev.map((d, i) => (
      i === dIdx ? { ...d, exercises: [...d.exercises, newExercise()] } : d
    )))
  }
  const removeExercise = (dIdx, eIdx) => {
    setDays((prev) => prev.map((d, i) => (
      i === dIdx ? { ...d, exercises: d.exercises.filter((_, j) => j !== eIdx) } : d
    )))
  }

  const toggleTarget = (dIdx, eIdx, slug) => {
    setDays((prev) => prev.map((d, i) => {
      if (i !== dIdx) return d
      const exercises = d.exercises.map((ex, j) => {
        if (j !== eIdx) return ex
        const existing = ex.targets.find((t0) => t0.slug === slug)
        const targets = existing
          ? ex.targets.filter((t0) => t0.slug !== slug)
          : [...ex.targets, { slug, intensity: 'medium' }]
        return { ...ex, targets }
      })
      return { ...d, exercises }
    }))
  }

  const setTargetIntensity = (dIdx, eIdx, slug, intensity) => {
    setDays((prev) => prev.map((d, i) => {
      if (i !== dIdx) return d
      const exercises = d.exercises.map((ex, j) => {
        if (j !== eIdx) return ex
        const targets = ex.targets.map((t0) => (
          t0.slug === slug ? { ...t0, intensity } : t0
        ))
        return { ...ex, targets }
      })
      return { ...d, exercises }
    }))
  }

  const validate = () => {
    if (showEn && !name.trim()) return t.workouts_err_name_en || 'English plan name is required.'
    if (showKa && !nameKa.trim()) return t.workouts_err_name_ka || 'Georgian plan name is required.'
    if (showEn && !description.trim()) return t.workouts_err_desc_en || 'English description is required.'
    if (showKa && !descriptionKa.trim()) return t.workouts_err_desc_ka || 'Georgian description is required.'

    for (let i = 0; i < days.length; i++) {
      const d = days[i]
      if (showEn && !d.name.trim()) return `${t.workouts_err_day_name_en || 'Day name (English) required for Day'} ${i + 1}.`
      if (showKa && !d.name_ka.trim()) return `${t.workouts_err_day_name_ka || 'Day name (Georgian) required for Day'} ${i + 1}.`
      if (d.exercises.length === 0) return `${t.workouts_err_day_empty || 'Add at least one exercise to Day'} ${i + 1}.`
      for (let j = 0; j < d.exercises.length; j++) {
        const e = d.exercises[j]
        if (showEn && !e.name.trim()) return `${t.workouts_err_ex_name_en || 'English exercise name required for Day'} ${i + 1}, #${j + 1}.`
        if (showKa && !e.name_ka.trim()) return `${t.workouts_err_ex_name_ka || 'Georgian exercise name required for Day'} ${i + 1}, #${j + 1}.`
        if (Number(e.rep_low) > Number(e.rep_high)) {
          return `${t.workouts_err_reps || 'Low reps cannot exceed high reps in Day'} ${i + 1}, #${j + 1}.`
        }
        if (e.targets.length === 0) {
          return `${t.workouts_err_targets || 'Select at least one muscle target in Day'} ${i + 1}, #${j + 1}.`
        }
      }
    }
    return null
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    const err = validate()
    if (err) return setError(err)

    const payload = {
      name: name.trim() || nameKa.trim(),
      name_ka: nameKa.trim() || null,
      description: description.trim() || descriptionKa.trim(),
      description_ka: descriptionKa.trim() || null,
      days_per_week: daysPerWeek,
      split_type: splitType.trim() || 'custom',
      level,
      days: days.map((d, i) => ({
        day_number: i + 1,
        name: d.name.trim() || d.name_ka.trim(),
        name_ka: d.name_ka.trim() || null,
        focus: d.focus.trim() || null,
        exercises: d.exercises.map((ex) => ({
          name: ex.name.trim() || ex.name_ka.trim(),
          name_ka: ex.name_ka.trim() || null,
          description: ex.description.trim(),
          description_ka: ex.description_ka.trim() || null,
          sets: Number(ex.sets) || 1,
          rep_low: Number(ex.rep_low) || 1,
          rep_high: Number(ex.rep_high) || 1,
          rest_seconds: Number(ex.rest_seconds) || 60,
          primary_purpose: ex.primary_purpose,
          muscle_group: ex.muscle_group,
          muscle_targets: ex.targets,
        })),
      })),
    }

    const fd = new FormData()
    fd.append('payload', JSON.stringify(payload))
    if (image) fd.append('image', image)

    setSubmitting(true)
    try {
      const r = await api.post('/workouts', fd)
      onCreated?.(r.data)
      onClose?.()
    } catch (e2) {
      const detail = e2.response?.data?.detail
      setError(typeof detail === 'string' ? detail : (t.workouts_err_generic || 'Could not create workout plan.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="add-workout-modal" onClick={(e) => e.stopPropagation()}>
        <div className="add-workout-header">
          <h2>{t.workouts_add_title || 'Create a Workout Plan'}</h2>
          <button className="meal-detail-close add-meal-close" onClick={onClose}>✕</button>
        </div>

        <form className="add-workout-form" onSubmit={handleSubmit}>
          <section className="add-workout-section">
            <h3 className="add-workout-section-title">
              1. {t.workouts_add_basics || 'Basics'}
            </h3>

            <div className="add-meal-field">
              <label>{t.meals_lang_choice || 'Language'}</label>
              <div className="add-meal-lang-pills">
                {LANG_OPTIONS.map((o) => (
                  <button
                    key={o.value}
                    type="button"
                    className={`add-meal-lang-pill${langChoice === o.value ? ' active' : ''}`}
                    onClick={() => setLangChoice(o.value)}
                  >
                    {t[o.labelKey] || o.value}
                  </button>
                ))}
              </div>
            </div>

            {showEn && (
              <>
                <div className="add-meal-field">
                  <label>{t.workouts_add_name || 'Plan name (English)'}</label>
                  <input
                    type="text" value={name} onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Push / Pull / Legs"
                  />
                </div>
                <div className="add-meal-field">
                  <label>{t.workouts_add_desc || 'Plan description (English)'}</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={4}
                    placeholder={t.workouts_add_desc_hint || 'Short summary of goals, target audience, and how the split is structured.'}
                  />
                </div>
              </>
            )}

            {showKa && (
              <>
                <div className="add-meal-field">
                  <label>{t.workouts_add_name_ka || 'Plan name (Georgian)'}</label>
                  <input
                    type="text" value={nameKa} onChange={(e) => setNameKa(e.target.value)}
                    placeholder="მაგ. Push / Pull / Legs"
                  />
                </div>
                <div className="add-meal-field">
                  <label>{t.workouts_add_desc_ka || 'Plan description (Georgian)'}</label>
                  <textarea
                    value={descriptionKa}
                    onChange={(e) => setDescriptionKa(e.target.value)}
                    rows={4}
                    placeholder="მოკლედ მიზნები და სტრუქტურა"
                  />
                </div>
              </>
            )}

            <div className="add-workout-grid-3">
              <div className="add-meal-field">
                <label>{t.workouts_freq_prompt || 'Days per week'}</label>
                <select
                  value={daysPerWeek}
                  onChange={(e) => setDaysPerWeek(Number(e.target.value))}
                >
                  {[1, 2, 3, 4, 5, 6, 7].map((n) => (
                    <option key={n} value={n}>{n}× / {t.workouts_week || 'week'}</option>
                  ))}
                </select>
              </div>
              <div className="add-meal-field">
                <label>{t.workouts_add_split || 'Split label'}</label>
                <input
                  type="text" value={splitType}
                  onChange={(e) => setSplitType(e.target.value)}
                  placeholder="custom, ppl, upper_lower…"
                />
              </div>
              <div className="add-meal-field">
                <label>{t.workouts_add_level || 'Difficulty'}</label>
                <select value={level} onChange={(e) => setLevel(e.target.value)}>
                  {LEVEL_OPTIONS.map((o) => (
                    <option key={o.value} value={o.value}>
                      {t[o.labelKey] || o.fallback}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="add-meal-field">
              <label>{t.workouts_add_image || 'Main image (optional)'}</label>
              <div className="add-meal-image-row">
                <label className="add-meal-image-btn">
                  {preview ? '✓ Change image' : '📷 Choose image'}
                  <input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleImage} hidden />
                </label>
                {preview && (
                  <img src={preview} alt="Preview" className="add-meal-image-preview" />
                )}
              </div>
            </div>
          </section>

          <section className="add-workout-section">
            <h3 className="add-workout-section-title">
              2. {t.workouts_add_days || 'Training days'}
            </h3>

            <div className="add-workout-days">
              {days.map((day, dIdx) => (
                <DayBuilder
                  key={dIdx}
                  day={day}
                  dIdx={dIdx}
                  showEn={showEn}
                  showKa={showKa}
                  appLang={appLang}
                  t={t}
                  onUpdateDay={(patch) => updateDay(dIdx, patch)}
                  onUpdateExercise={(eIdx, patch) => updateExercise(dIdx, eIdx, patch)}
                  onAddExercise={() => addExercise(dIdx)}
                  onRemoveExercise={(eIdx) => removeExercise(dIdx, eIdx)}
                  onToggleTarget={(eIdx, slug) => toggleTarget(dIdx, eIdx, slug)}
                  onSetIntensity={(eIdx, slug, intensity) =>
                    setTargetIntensity(dIdx, eIdx, slug, intensity)}
                />
              ))}
            </div>
          </section>

          {error && <p className="add-meal-error">{error}</p>}

          <div className="add-meal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              {t.ch_cancel || 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting
                ? (t.workouts_submitting || 'Creating…')
                : (t.workouts_submit || 'Create plan')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}


function DayBuilder({
  day, dIdx, showEn, showKa, appLang, t,
  onUpdateDay, onUpdateExercise, onAddExercise, onRemoveExercise,
  onToggleTarget, onSetIntensity,
}) {
  return (
    <div className="add-workout-day">
      <div className="add-workout-day-head">
        <span className="add-workout-day-badge">
          {t.workouts_day || 'Day'} {day.day_number}
        </span>
      </div>

      <div className="add-workout-grid-2">
        {showEn && (
          <div className="add-meal-field">
            <label>{t.workouts_add_day_name || 'Day name (English)'}</label>
            <input
              type="text" value={day.name}
              onChange={(e) => onUpdateDay({ name: e.target.value })}
              placeholder="e.g. Push Day"
            />
          </div>
        )}
        {showKa && (
          <div className="add-meal-field">
            <label>{t.workouts_add_day_name_ka || 'Day name (Georgian)'}</label>
            <input
              type="text" value={day.name_ka}
              onChange={(e) => onUpdateDay({ name_ka: e.target.value })}
              placeholder="მაგ. Push დღე"
            />
          </div>
        )}
        <div className="add-meal-field">
          <label>{t.workouts_add_day_focus || 'Focus (optional)'}</label>
          <input
            type="text" value={day.focus}
            onChange={(e) => onUpdateDay({ focus: e.target.value })}
            placeholder="chest, triceps, shoulders…"
          />
        </div>
      </div>

      <div className="add-workout-exercises">
        {day.exercises.map((ex, eIdx) => (
          <ExerciseBuilder
            key={eIdx}
            exercise={ex}
            eIdx={eIdx}
            showEn={showEn}
            showKa={showKa}
            appLang={appLang}
            t={t}
            onUpdate={(patch) => onUpdateExercise(eIdx, patch)}
            onRemove={() => onRemoveExercise(eIdx)}
            onToggleTarget={(slug) => onToggleTarget(eIdx, slug)}
            onSetIntensity={(slug, intensity) => onSetIntensity(eIdx, slug, intensity)}
            canRemove={day.exercises.length > 1}
          />
        ))}

        <button
          type="button"
          className="add-workout-add-exercise"
          onClick={onAddExercise}
        >
          ➕ {t.workouts_add_exercise || 'Add exercise'}
        </button>
      </div>
    </div>
  )
}


function ExerciseBuilder({
  exercise, eIdx, showEn, showKa, appLang, t,
  onUpdate, onRemove, onToggleTarget, onSetIntensity, canRemove,
}) {
  const ex = exercise
  const previewGender = useMemo(() => {
    try {
      const u = JSON.parse(localStorage.getItem('user') || 'null')
      return u?.gender === 'female' ? 'female' : 'male'
    } catch { return 'male' }
  }, [])

  // Auto-derive primary_purpose when reps change (user can still override).
  useEffect(() => {
    const derived = purposeFromReps(ex.rep_low, ex.rep_high)
    if (derived !== ex.primary_purpose) onUpdate({ primary_purpose: derived })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ex.rep_low, ex.rep_high])

  return (
    <div className="add-workout-exercise">
      <div className="add-workout-exercise-head">
        <span className="add-workout-exercise-num">#{eIdx + 1}</span>
        {canRemove && (
          <button
            type="button"
            className="add-workout-remove"
            onClick={onRemove}
            aria-label="Remove exercise"
          >✕</button>
        )}
      </div>

      <div className="add-workout-grid-2">
        {showEn && (
          <div className="add-meal-field">
            <label>{t.workouts_add_ex_name || 'Exercise name (English)'}</label>
            <input
              type="text" value={ex.name}
              onChange={(e) => onUpdate({ name: e.target.value })}
              placeholder="e.g. Barbell Bench Press"
            />
          </div>
        )}
        {showKa && (
          <div className="add-meal-field">
            <label>{t.workouts_add_ex_name_ka || 'Exercise name (Georgian)'}</label>
            <input
              type="text" value={ex.name_ka}
              onChange={(e) => onUpdate({ name_ka: e.target.value })}
              placeholder="მაგ. შტანგით ბენჩ პრესი"
            />
          </div>
        )}
      </div>

      {showEn && (
        <div className="add-meal-field">
          <label>{t.workouts_add_ex_desc || 'Cue / description (English, optional)'}</label>
          <textarea
            value={ex.description}
            onChange={(e) => onUpdate({ description: e.target.value })}
            rows={2}
          />
        </div>
      )}
      {showKa && (
        <div className="add-meal-field">
          <label>{t.workouts_add_ex_desc_ka || 'Cue / description (Georgian, optional)'}</label>
          <textarea
            value={ex.description_ka}
            onChange={(e) => onUpdate({ description_ka: e.target.value })}
            rows={2}
          />
        </div>
      )}

      <div className="add-workout-grid-5">
        <div className="add-meal-field">
          <label>{t.workouts_sets || 'Sets'}</label>
          <input
            type="number" min="1" max="20" value={ex.sets}
            onChange={(e) => onUpdate({ sets: e.target.value })}
          />
        </div>
        <div className="add-meal-field">
          <label>{t.workouts_add_rep_low || 'Reps (low)'}</label>
          <input
            type="number" min="1" max="100" value={ex.rep_low}
            onChange={(e) => onUpdate({ rep_low: e.target.value })}
          />
        </div>
        <div className="add-meal-field">
          <label>{t.workouts_add_rep_high || 'Reps (high)'}</label>
          <input
            type="number" min="1" max="100" value={ex.rep_high}
            onChange={(e) => onUpdate({ rep_high: e.target.value })}
          />
        </div>
        <div className="add-meal-field">
          <label>{t.workouts_add_rest || 'Rest (sec)'}</label>
          <input
            type="number" min="0" max="1200" step="5" value={ex.rest_seconds}
            onChange={(e) => onUpdate({ rest_seconds: e.target.value })}
          />
        </div>
        <div className="add-meal-field">
          <label>{t.workouts_add_purpose || 'Goal'}</label>
          <select
            value={ex.primary_purpose}
            onChange={(e) => onUpdate({ primary_purpose: e.target.value })}
          >
            {PURPOSE_OPTIONS.map((p) => (
              <option key={p.value} value={p.value}>
                {p.emoji} {appLang === 'ka' ? p.ka : p.en}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="add-meal-field">
        <label>{t.workouts_add_muscle_group || 'Primary muscle group'}</label>
        <select
          value={ex.muscle_group}
          onChange={(e) => onUpdate({ muscle_group: e.target.value })}
        >
          {MUSCLE_GROUP_OPTIONS.map((m) => (
            <option key={m} value={m}>
              {t[`workouts_muscle_${m}`] || m}
            </option>
          ))}
        </select>
      </div>

      <div className="add-workout-targets">
        <label className="add-workout-targets-label">
          {t.workouts_add_targets || 'Targeted muscles + intensity'}
        </label>
        <p className="add-workout-targets-hint">
          {t.workouts_add_targets_hint
           || 'Tick every muscle this exercise works and set how hard it hits each — this controls the red shading on the map.'}
        </p>

        <div className="add-workout-targets-grid">
          {MUSCLE_SLUGS.map((m) => {
            const selected = ex.targets.find((tg) => tg.slug === m.slug)
            return (
              <div
                key={m.slug}
                className={`add-workout-target-chip${selected ? ' selected' : ''}`}
              >
                <button
                  type="button"
                  className="add-workout-target-toggle"
                  onClick={() => onToggleTarget(m.slug)}
                >
                  {selected ? '✓' : '+'} {appLang === 'ka' ? m.ka : m.en}
                </button>
                {selected && (
                  <div className="add-workout-target-intensities">
                    {INTENSITY_OPTIONS.map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        className={`add-workout-target-int int-${opt.value}${
                          selected.intensity === opt.value ? ' active' : ''
                        }`}
                        onClick={() => onSetIntensity(m.slug, opt.value)}
                      >
                        {appLang === 'ka' ? opt.ka : opt.en}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {ex.targets.length > 0 && (
          <div className="add-workout-target-preview">
            <ExerciseMuscleMap targets={ex.targets} gender={previewGender} />
          </div>
        )}
      </div>
    </div>
  )
}
