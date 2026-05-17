import StarRating from './StarRating'
import { resolveAssetUrl } from '../../api/client'

const GOAL_EMOJI = {
  cut: '🔥',
  bulk: '💪',
  maintain: '⚖️',
  general: '🍽️',
  cheat: '🍫',
}

export default function MealCard({ meal, t, onRate, onView, appLang }) {
  const name = appLang === 'ka' && meal.name_ka ? meal.name_ka : meal.name
  const rawDesc = appLang === 'ka' && meal.description_ka ? meal.description_ka : meal.description
  const desc = rawDesc || ''
  const firstLine = desc.split('\n')[0] || ''
  const short = firstLine.length > 100 ? firstLine.slice(0, 100) + '…' : firstLine

  return (
    <div className="meal-card" onClick={() => onView(meal)}>
      <div
        className="meal-card-img"
        style={{ backgroundImage: meal.image_url ? `url(${resolveAssetUrl(meal.image_url)})` : undefined }}
      >
        <span className="meal-card-goal-badge">
          {GOAL_EMOJI[meal.goal] || '🍽️'} {t[`meals_goal_${meal.goal}`] || meal.goal}
        </span>
      </div>

      <div className="meal-card-body">
        <h3 className="meal-card-name">{name}</h3>
        <p className="meal-card-desc">
          {short}
          {desc.length > 100 && (
            <span className="meal-card-more"> {t.meals_read_more || 'More'}</span>
          )}
        </p>

        <div className="meal-card-macros">
          <span className="macro macro-cal">{meal.calories} kcal</span>
          <span className="macro macro-pro">{meal.protein}g P</span>
          <span className="macro macro-carb">{meal.carbs}g C</span>
          <span className="macro macro-fat">{meal.fat}g F</span>
        </div>

        <div className="meal-card-footer">
          <div className="meal-card-rating">
            <StarRating rating={meal.rating} size={16} />
            <span className="meal-card-rating-count">
              {meal.rating.toFixed(1)} ({meal.rating_count})
            </span>
          </div>
          <span className="meal-card-views">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            {meal.views}
          </span>
        </div>
      </div>
    </div>
  )
}
