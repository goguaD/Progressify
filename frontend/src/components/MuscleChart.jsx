import { useMemo } from 'react'
import { LEVELS, LEVEL_COLORS } from './BodyFigure'

const GRAY = '#9ca3af'
const SIZE = 160
const CX = SIZE / 2
const CY = SIZE / 2
const R = 62

function polarToCart(cx, cy, r, angleDeg) {
  const rad = ((angleDeg - 90) * Math.PI) / 180
  return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)]
}

function arcPath(cx, cy, r, startAngle, endAngle) {
  const start = polarToCart(cx, cy, r, startAngle)
  const end = polarToCart(cx, cy, r, endAngle)
  const large = endAngle - startAngle > 180 ? 1 : 0
  return `M${cx},${cy} L${start[0]},${start[1]} A${r},${r} 0 ${large} 1 ${end[0]},${end[1]} Z`
}

export default function MuscleChart({ muscleLevels = {}, totalGroups, t }) {
  const { slices, pcts } = useMemo(() => {
    const counts = { none: 0 }
    LEVELS.forEach((l) => { counts[l] = 0 })

    Object.values(muscleLevels).forEach((lvl) => {
      if (lvl && counts[lvl] !== undefined) counts[lvl]++
      else counts.none++
    })
    counts.none += totalGroups - Object.values(muscleLevels).filter((v) => v).length

    const total = totalGroups
    const pcts = {}
    const order = [...LEVELS, 'none']
    order.forEach((k) => { pcts[k] = Math.round((counts[k] / total) * 100) })

    let angle = 0
    const slices = []
    order.forEach((key) => {
      if (counts[key] === 0) return
      const sweep = (counts[key] / total) * 360
      if (sweep >= 360) {
        slices.push({ key, full: true })
      } else {
        slices.push({ key, start: angle, end: angle + sweep })
      }
      angle += sweep
    })

    return { slices, pcts }
  }, [muscleLevels, totalGroups])

  return (
    <div className="muscle-chart">
      <svg viewBox={`0 0 ${SIZE} ${SIZE}`} className="muscle-chart-svg">
        {slices.map((s) =>
          s.full ? (
            <circle
              key={s.key}
              cx={CX} cy={CY} r={R}
              fill={s.key === 'none' ? GRAY : LEVEL_COLORS[s.key]}
            />
          ) : (
            <path
              key={s.key}
              d={arcPath(CX, CY, R, s.start, s.end)}
              fill={s.key === 'none' ? GRAY : LEVEL_COLORS[s.key]}
            />
          )
        )}
        <circle cx={CX} cy={CY} r={30} fill="var(--bg-card)" />
      </svg>

      <div className="muscle-chart-labels">
        {LEVELS.map((lvl) => (
          pcts[lvl] > 0 && (
            <div key={lvl} className="chart-label-row">
              <span className="chart-label-dot" style={{ background: LEVEL_COLORS[lvl] }} />
              <span className="chart-label-text">{t[`level_${lvl}`]}</span>
              <span className="chart-label-pct">{pcts[lvl]}%</span>
            </div>
          )
        ))}
        {pcts.none > 0 && (
          <div className="chart-label-row">
            <span className="chart-label-dot" style={{ background: GRAY }} />
            <span className="chart-label-text">{t.level_none || 'No data'}</span>
            <span className="chart-label-pct">{pcts.none}%</span>
          </div>
        )}
      </div>
    </div>
  )
}
