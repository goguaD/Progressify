import StarRating from '../meals/StarRating'
import { resolveAssetUrl } from '../../api/client'

const SPLIT_EMOJI = {
  full_body: '🏋️',
  ppl: '💪',
  upper_lower: '🔥',
  ppl_upper: '⚡',
  bro_split: '🦾',
  ppl_upper_lower: '🚀',
}

const LEVEL_BADGE = {
  beginner: { en: 'Beginner', ka: 'დამწყები', cls: 'beginner' },
  intermediate: { en: 'Intermediate', ka: 'საშუალო', cls: 'intermediate' },
  advanced: { en: 'Advanced', ka: 'მოწინავე', cls: 'advanced' },
}

export default function WorkoutCard({ plan, t, onView, appLang }) {
  const name = appLang === 'ka' && plan.name_ka ? plan.name_ka : plan.name
  const rawDesc = appLang === 'ka' && plan.description_ka ? plan.description_ka : plan.description
  const desc = rawDesc || ''
  const short = desc.length > 130 ? desc.slice(0, 130) + '…' : desc

  const level = LEVEL_BADGE[plan.level] || LEVEL_BADGE.intermediate
  const levelLabel = appLang === 'ka' ? level.ka : level.en

  return (
    <div className="workout-card" onClick={() => onView(plan)}>
      <div
        className="workout-card-img"
        style={{ backgroundImage: plan.image_url ? `url(${resolveAssetUrl(plan.image_url)})` : undefined }}
      >
        <span className="workout-card-days-badge">
          {SPLIT_EMOJI[plan.split_type] || '🏋️'} {plan.days_per_week}× / {t.workouts_week || 'week'}
        </span>
        <span className={`workout-card-level-badge ${level.cls}`}>
          {levelLabel}
        </span>
      </div>

      <div className="workout-card-body">
        <h3 className="workout-card-name">{name}</h3>
        <p className="workout-card-desc">{short}</p>

        <div className="workout-card-footer">
          <div className="workout-card-rating">
            <StarRating rating={plan.rating} size={16} />
            <span className="workout-card-rating-count">
              {plan.rating.toFixed(1)} ({plan.rating_count})
            </span>
          </div>
          <span className="workout-card-views">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
            {plan.views}
          </span>
        </div>
      </div>
    </div>
  )
}
