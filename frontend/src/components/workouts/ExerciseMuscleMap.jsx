import Body from 'react-muscle-highlighter'

// 4-step red intensity ramp for the body-highlighter library. Index 0 is
// unused; we map intensities to colors as:
//   low     → #fca5a5  (light)
//   medium  → #ef4444  (mid)
//   high    → #b91c1c  (deep)
const RED_RAMP = ['#fca5a5', '#fca5a5', '#ef4444', '#b91c1c']

const INTENSITY_RANK = { low: 1, medium: 2, high: 3 }

function FigureView({ data, side, gender }) {
  return (
    <div className="exercise-muscle-figure">
      <Body
        data={data}
        side={side}
        gender={gender === 'female' ? 'female' : 'male'}
        scale={0.9}
        colors={RED_RAMP}
        defaultFill="var(--muscle-base)"
        defaultStroke="var(--muscle-stroke)"
        defaultStrokeWidth={0.6}
        border="var(--muscle-stroke)"
      />
    </div>
  )
}

export default function ExerciseMuscleMap({
  primary = [],
  secondary = [],
  targets = null,
  gender = 'male',
}) {
  // `targets` (when provided) takes precedence over primary/secondary —
  // this is how user-submitted exercises pass their {slug, intensity} list.
  let data
  if (Array.isArray(targets) && targets.length > 0) {
    data = targets.map((t) => ({
      slug: t.slug,
      intensity: INTENSITY_RANK[t.intensity] || 2,
    }))
  } else {
    data = [
      ...secondary.map((slug) => ({ slug, intensity: INTENSITY_RANK.low })),
      ...primary.map((slug) => ({ slug, intensity: INTENSITY_RANK.high })),
    ]
  }

  return (
    <div className="exercise-muscle-map">
      <FigureView data={data} side="front" gender={gender} />
      <FigureView data={data} side="back" gender={gender} />
    </div>
  )
}
