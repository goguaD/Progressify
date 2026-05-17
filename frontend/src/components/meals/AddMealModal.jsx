import { useState } from 'react'
import api from '../../api/client'

const GOAL_OPTIONS = [
  { value: 'cut', label: { en: '🔥 Cut', ka: '🔥 წონის კლება' } },
  { value: 'bulk', label: { en: '💪 Bulk', ka: '💪 მასის მომატება' } },
  { value: 'maintain', label: { en: '⚖️ Maintain', ka: '⚖️ შენარჩუნება' } },
  { value: 'cheat', label: { en: '🍫 Cheat Meal', ka: '🍫 ჩითი' } },
  { value: 'general', label: { en: '🍽️ General', ka: '🍽️ ზოგადი' } },
]

const LANG_OPTIONS = [
  { value: 'en', labelKey: 'meals_lang_en' },
  { value: 'ka', labelKey: 'meals_lang_ka' },
  { value: 'both', labelKey: 'meals_lang_both' },
]

const EMPTY = {
  langChoice: 'en',
  name: '', description: '',
  name_ka: '', description_ka: '',
  goal: 'general',
  calories: '', protein: '', carbs: '', fat: '', fiber: '', sugar: '',
  image: null,
}

export default function AddMealModal({ t, appLang, onClose, onAdded }) {
  const [form, setForm] = useState(EMPTY)
  const [preview, setPreview] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const showEn = form.langChoice === 'en' || form.langChoice === 'both'
  const showKa = form.langChoice === 'ka' || form.langChoice === 'both'

  const handleImage = (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    set('image', file)
    setPreview(URL.createObjectURL(file))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    const hasEnName = form.name.trim()
    const hasKaName = form.name_ka.trim()
    if (showEn && !hasEnName) return setError('English name is required.')
    if (showKa && !hasKaName) return setError('Georgian name is required.')
    if (showEn && !form.description.trim()) return setError('English description is required.')
    if (showKa && !form.description_ka.trim()) return setError('Georgian description is required.')
    if (!form.calories || !form.protein || !form.carbs || !form.fat) {
      return setError('Calories, protein, carbs, and fat are required.')
    }

    const fd = new FormData()
    fd.append('name', form.name.trim() || form.name_ka.trim())
    fd.append('description', form.description.trim() || form.description_ka.trim())
    fd.append('goal', form.goal)
    fd.append('calories', form.calories)
    fd.append('protein', form.protein)
    fd.append('carbs', form.carbs)
    fd.append('fat', form.fat)
    if (form.fiber) fd.append('fiber', form.fiber)
    if (form.sugar) fd.append('sugar', form.sugar)
    if (form.name_ka.trim()) fd.append('name_ka', form.name_ka.trim())
    if (form.description_ka.trim()) fd.append('description_ka', form.description_ka.trim())
    if (form.image) fd.append('image', form.image)

    setSubmitting(true)
    try {
      const r = await api.post('/meals', fd, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      onAdded(r.data)
      onClose()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to add meal.')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="add-meal-modal" onClick={e => e.stopPropagation()}>
        <div className="add-meal-header">
          <h2>{t.meals_add_title || 'Add New Meal'}</h2>
          <button className="meal-detail-close add-meal-close" onClick={onClose}>✕</button>
        </div>

        <form className="add-meal-form" onSubmit={handleSubmit}>
          {/* Language choice */}
          <div className="add-meal-field">
            <label>{t.meals_lang_choice || 'Language'}</label>
            <div className="add-meal-lang-pills">
              {LANG_OPTIONS.map(o => (
                <button
                  key={o.value}
                  type="button"
                  className={`add-meal-lang-pill${form.langChoice === o.value ? ' active' : ''}`}
                  onClick={() => set('langChoice', o.value)}
                >
                  {t[o.labelKey] || o.value}
                </button>
              ))}
            </div>
          </div>

          {/* English fields */}
          {showEn && (
            <>
              <div className="add-meal-field">
                <label>{t.meals_name || 'Meal name'}</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={e => set('name', e.target.value)}
                  placeholder="e.g. Grilled Chicken Salad"
                />
              </div>
              <div className="add-meal-field">
                <label>{t.meals_description || 'Description'}</label>
                <textarea
                  value={form.description}
                  onChange={e => set('description', e.target.value)}
                  placeholder={t.meals_description_hint || 'Include ingredients, portions, temperature, cooking steps…'}
                  rows={6}
                />
              </div>
            </>
          )}

          {/* Georgian fields */}
          {showKa && (
            <>
              <div className="add-meal-field">
                <label>{t.meals_name_ka || 'Meal name (Georgian)'}</label>
                <input
                  type="text"
                  value={form.name_ka}
                  onChange={e => set('name_ka', e.target.value)}
                  placeholder="მაგ. შემწვარი ქათმის სალათი"
                />
              </div>
              <div className="add-meal-field">
                <label>{t.meals_description_ka || 'Description (Georgian)'}</label>
                <textarea
                  value={form.description_ka}
                  onChange={e => set('description_ka', e.target.value)}
                  placeholder="მიუთითეთ ინგრედიენტები, პორციები, ტემპერატურა…"
                  rows={6}
                />
              </div>
            </>
          )}

          {/* Goal */}
          <div className="add-meal-field">
            <label>{t.meals_goal_label || 'Meal type'}</label>
            <select value={form.goal} onChange={e => set('goal', e.target.value)}>
              {GOAL_OPTIONS.map(o => (
                <option key={o.value} value={o.value}>
                  {o.label[appLang] || o.label.en}
                </option>
              ))}
            </select>
          </div>

          {/* Image */}
          <div className="add-meal-field">
            <label>{t.meals_image || 'Meal photo'}</label>
            <div className="add-meal-image-row">
              <label className="add-meal-image-btn">
                {preview ? '✓ Change photo' : '📷 Choose photo'}
                <input type="file" accept="image/png,image/jpeg,image/webp" onChange={handleImage} hidden />
              </label>
              {preview && (
                <img src={preview} alt="Preview" className="add-meal-image-preview" />
              )}
            </div>
          </div>

          {/* Nutrients */}
          <div className="add-meal-field">
            <label>{t.meals_calories || 'Calories'} / {t.meals_protein || 'Protein'} / {t.meals_carbs || 'Carbs'} / {t.meals_fat || 'Fat'}</label>
            <div className="add-meal-nutrients-grid">
              <input type="number" placeholder={t.meals_calories || 'Calories'} min="0"
                value={form.calories} onChange={e => set('calories', e.target.value)} />
              <input type="number" placeholder={t.meals_protein || 'Protein (g)'} min="0" step="0.1"
                value={form.protein} onChange={e => set('protein', e.target.value)} />
              <input type="number" placeholder={t.meals_carbs || 'Carbs (g)'} min="0" step="0.1"
                value={form.carbs} onChange={e => set('carbs', e.target.value)} />
              <input type="number" placeholder={t.meals_fat || 'Fat (g)'} min="0" step="0.1"
                value={form.fat} onChange={e => set('fat', e.target.value)} />
              <input type="number" placeholder={t.meals_fiber || 'Fiber (g)'} min="0" step="0.1"
                value={form.fiber} onChange={e => set('fiber', e.target.value)} />
              <input type="number" placeholder={t.meals_sugar || 'Sugar (g)'} min="0" step="0.1"
                value={form.sugar} onChange={e => set('sugar', e.target.value)} />
            </div>
          </div>

          {error && <p className="add-meal-error">{error}</p>}

          <div className="add-meal-actions">
            <button type="button" className="btn btn-secondary" onClick={onClose}>
              {t.ch_cancel || 'Cancel'}
            </button>
            <button type="submit" className="btn btn-primary" disabled={submitting}>
              {submitting ? (t.meals_submitting || 'Adding…') : (t.meals_submit || 'Add Meal')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
