import { useState } from 'react'
import StarRating from './StarRating'

const GOAL_LABELS = {
  cut: { en: '🔥 Fat Loss / Cut', ka: '🔥 წონის კლება' },
  bulk: { en: '💪 Muscle Gain / Bulk', ka: '💪 მასის მომატება' },
  maintain: { en: '⚖️ Maintenance', ka: '⚖️ შენარჩუნება' },
  general: { en: '🍽️ General', ka: '🍽️ ზოგადი' },
}

export default function MealDetail({ meal, t, onClose, onRate, appLang }) {
  const [lang, setLang] = useState(appLang || 'en')

  const name = lang === 'ka' && meal.name_ka ? meal.name_ka : meal.name
  const description = lang === 'ka' && meal.description_ka ? meal.description_ka : meal.description
  const goalLabel = GOAL_LABELS[meal.goal]?.[lang] || GOAL_LABELS[meal.goal]?.en || meal.goal
  const noTranslation = lang === 'ka' && !meal.description_ka

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="meal-detail-card" onClick={e => e.stopPropagation()}>
        {meal.image_url && (
          <div
            className="meal-detail-hero"
            style={{ backgroundImage: `url(${meal.image_url})` }}
          >
            <button className="meal-detail-close" onClick={onClose}>✕</button>
            <div className="meal-detail-lang-toggle">
              <button
                className={`meal-lang-btn${lang === 'en' ? ' active' : ''}`}
                onClick={() => setLang('en')}
              >
                EN
              </button>
              <button
                className={`meal-lang-btn${lang === 'ka' ? ' active' : ''}`}
                onClick={() => setLang('ka')}
              >
                KA
              </button>
            </div>
          </div>
        )}
        {!meal.image_url && (
          <div className="meal-detail-nohero-bar">
            <button className="meal-detail-close meal-detail-close-nohero" onClick={onClose}>✕</button>
            <div className="meal-detail-lang-toggle meal-detail-lang-nohero">
              <button
                className={`meal-lang-btn${lang === 'en' ? ' active' : ''}`}
                onClick={() => setLang('en')}
              >
                EN
              </button>
              <button
                className={`meal-lang-btn${lang === 'ka' ? ' active' : ''}`}
                onClick={() => setLang('ka')}
              >
                KA
              </button>
            </div>
          </div>
        )}

        <div className="meal-detail-body">
          <span className="meal-detail-goal">{goalLabel}</span>
          <h2 className="meal-detail-name">{name}</h2>

          {noTranslation && (
            <p className="meal-detail-no-trans">
              {t.meals_no_translation || 'Georgian translation not available yet.'}
            </p>
          )}

          <div className="meal-detail-desc">
            {description.split('\n').map((line, i) => (
              <p key={i} className={line === '' ? 'meal-desc-gap' : undefined}>
                {line}
              </p>
            ))}
          </div>

          <div className="meal-detail-macros">
            <MacroBlock label={lang === 'ka' ? 'კალორია' : 'Calories'} value={meal.calories} unit="kcal" accent />
            <MacroBlock label={lang === 'ka' ? 'ცილა' : 'Protein'} value={meal.protein} unit="g" />
            <MacroBlock label={lang === 'ka' ? 'ნახშირწყალი' : 'Carbs'} value={meal.carbs} unit="g" />
            <MacroBlock label={lang === 'ka' ? 'ცხიმი' : 'Fat'} value={meal.fat} unit="g" />
            {meal.fiber != null && (
              <MacroBlock label={lang === 'ka' ? 'ბოჭკო' : 'Fiber'} value={meal.fiber} unit="g" />
            )}
            {meal.sugar != null && (
              <MacroBlock label={lang === 'ka' ? 'შაქარი' : 'Sugar'} value={meal.sugar} unit="g" />
            )}
          </div>

          <div className="meal-detail-stats">
            <div className="meal-detail-rating-section">
              <div className="meal-detail-avg-row">
                <span className="meal-detail-rating-label">
                  {lang === 'ka' ? 'საშუალო' : 'Average'}
                </span>
                <StarRating rating={meal.rating} size={18} />
                <span className="meal-detail-rating-text">
                  {meal.rating.toFixed(1)} ({meal.rating_count})
                </span>
              </div>
              <div className="meal-detail-my-row">
                <span className="meal-detail-rating-label">
                  {lang === 'ka' ? 'ჩემი შეფასება' : 'Your rating'}
                </span>
                <StarRating
                  rating={meal.my_rating || 0}
                  myRating={meal.my_rating}
                  onRate={(score) => onRate(meal.id, score)}
                  size={18}
                />
                {meal.my_rating != null && (
                  <span className="meal-detail-rating-text">{meal.my_rating.toFixed(1)}</span>
                )}
              </div>
            </div>
            <span className="meal-detail-views">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              {meal.views} {t.meals_views || 'views'}
            </span>
          </div>

          {meal.added_by_username && (
            <p className="meal-detail-author">
              {t.meals_added_by || 'Added by'} <strong>@{meal.added_by_username}</strong>
            </p>
          )}
        </div>
      </div>
    </div>
  )
}

function MacroBlock({ label, value, unit, accent }) {
  return (
    <div className={`macro-block${accent ? ' macro-block-accent' : ''}`}>
      <span className="macro-block-value">{value}<small>{unit}</small></span>
      <span className="macro-block-label">{label}</span>
    </div>
  )
}
