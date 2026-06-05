import { useState } from 'react'
import BodyFigure, { LEVELS, LEVEL_COLORS } from '../BodyFigure'
import MuscleChart from '../MuscleChart'
import OneRepMaxStats from './OneRepMaxStats'

const FRONT_MUSCLES = [
  'chest', 'biceps', 'deltoids', 'abs', 'obliques',
  'quadriceps', 'forearm', 'adductors', 'neck',
]

const BACK_MUSCLES = [
  'trapezius', 'upper_back', 'lower_back', 'triceps',
  'hamstring', 'calves', 'gluteal',
]

const ALL_MUSCLES = [...FRONT_MUSCLES, ...BACK_MUSCLES]

export default function AnatomySection({
  profile, t,
  editable = false,
  onUpdateLifts,
}) {
  const [view, setView] = useState('front')
  const muscleLevels = profile.muscle_levels || {}
  const hasData = Object.keys(muscleLevels).length > 0
  const lifts = profile.active_workout?.lifts || []

  return (
    <div className="anatomy-card">
      <div className="anatomy-header">
        <div>
          <h2 className="anatomy-title">{t.profile_anatomy} 🧬</h2>
          <p className="anatomy-sub">{t.profile_anatomy_sub}</p>
        </div>
        <div className="filter-tabs anatomy-tabs" role="tablist">
          {[
            { id: 'front', label: t.profile_view_front },
            { id: 'back',  label: t.profile_view_back  },
          ].map((opt) => (
            <button key={opt.id} role="tab" aria-selected={view === opt.id}
              className={`filter-tab ${view === opt.id ? 'active' : ''}`}
              onClick={() => setView(opt.id)}>
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      <div className="anatomy-body-row">
        <div className="anatomy-figure-col">
          <div className="anatomy-figure-wrap">
            <BodyFigure
              gender={profile.gender}
              view={view}
              muscles={muscleLevels}
            />
          </div>
          <MuscleChart
            muscleLevels={muscleLevels}
            totalGroups={ALL_MUSCLES.length}
            t={t}
          />
        </div>

        <div className="anatomy-legend">
          <h3 className="anatomy-legend-title">{t.muscle_legend_title}</h3>

          <div className="level-key">
            {LEVELS.map((lvl) => (
              <div key={lvl} className="level-key-item">
                <span className="level-dot" style={{ background: LEVEL_COLORS[lvl] }} />
                <span className="level-label">{t[`level_${lvl}`]}</span>
              </div>
            ))}
          </div>

          <div className="muscle-list">
            {(view === 'front' ? FRONT_MUSCLES : BACK_MUSCLES).map((slug) => {
              const key = slug === 'upper_back' ? 'upper-back' : slug === 'lower_back' ? 'lower-back' : slug
              const level = muscleLevels[key]
              return (
                <div key={slug} className="muscle-row">
                  <span className="muscle-name">{t[`muscle_${slug}`]}</span>
                  <span
                    className="muscle-level-badge"
                    style={level ? { background: LEVEL_COLORS[level], color: level === 'elite' ? '#1a1a1a' : '#fff' } : undefined}
                  >
                    {level ? t[`level_${level}`] : '—'}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        <OneRepMaxStats
          lifts={lifts}
          t={t}
          editable={editable}
          onUpdate={onUpdateLifts}
        />
      </div>

      <div className="anatomy-disclaimer">
        <span className="anatomy-disclaimer-icon">ℹ️</span>
        <span>
          {hasData
            ? (t.profile_anatomy_disclaimer
               || 'Development tiers are estimated from your bodyweight and self-reported one-rep maxes, calibrated against published strength standards for trained populations.')
            : (t.profile_anatomy_disclaimer_empty
               || 'Add a workout plan and submit your one-rep maxes to see your development tiers. Estimates use bodyweight and lift data calibrated against published strength standards.')}
        </span>
      </div>
    </div>
  )
}
