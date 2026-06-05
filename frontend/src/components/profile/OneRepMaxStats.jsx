import { LEVEL_COLORS } from '../BodyFigure'

export default function OneRepMaxStats({ lifts = [], t, appLang = 'en', editable = false, onUpdate }) {
  const tracked = lifts.filter((l) => l.weight_kg > 0)

  if (tracked.length === 0) {
    return (
      <aside className="orm-stats">
        <div className="orm-stats-head">
          <h3 className="orm-stats-title">{t.profile_orm_title || 'One-rep max statistics'}</h3>
          <p className="orm-stats-sub">
            {t.profile_orm_sub
             || 'Your top lifts are displayed here once you submit them.'}
          </p>
        </div>
        {editable && onUpdate && (
          <button className="btn btn-secondary orm-stats-update" onClick={onUpdate}>
            {t.profile_orm_set || 'Enter lifts'}
          </button>
        )}
      </aside>
    )
  }

  return (
    <aside className="orm-stats">
      <div className="orm-stats-head">
        <h3 className="orm-stats-title">{t.profile_orm_title || 'One-rep max statistics'}</h3>
        <p className="orm-stats-sub">
          {t.profile_orm_sub
           || 'Strength tiers are derived from your bodyweight-to-lift ratio.'}
        </p>
      </div>

      <ul className="orm-stats-list">
        {tracked.map((l) => {
          const level = l.level
          const color = level ? LEVEL_COLORS[level] : undefined
          return (
            <li key={l.exercise_name} className="orm-stats-row">
              <div className="orm-stats-meta">
                <span className="orm-stats-name">
                  {appLang === 'ka' && l.exercise_name_ka ? l.exercise_name_ka : l.exercise_name}
                </span>
                {level && (
                  <span
                    className="orm-stats-level"
                    style={{ background: color, color: level === 'elite' ? '#1a1a1a' : '#fff' }}
                  >
                    {t[`level_${level}`]}
                  </span>
                )}
                {!level && (
                  <span className="orm-stats-level orm-stats-level-na">
                    {t.profile_orm_no_standard || 'untracked'}
                  </span>
                )}
              </div>
              <div className="orm-stats-weight">
                <span className="orm-stats-weight-num">{Math.round(l.weight_kg * 10) / 10}</span>
                <span className="orm-stats-weight-unit">kg</span>
              </div>
            </li>
          )
        })}
      </ul>

      {editable && onUpdate && (
        <button className="btn btn-secondary orm-stats-update" onClick={onUpdate}>
          {t.profile_orm_update || 'Update lifts'}
        </button>
      )}
    </aside>
  )
}
