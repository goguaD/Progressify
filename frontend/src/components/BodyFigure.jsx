import Body from 'react-muscle-highlighter'

/**
 * Anatomy figure for the profile page.
 *
 * Renders a vector body with ~23 muscle groups (chest, biceps, triceps,
 * abs, deltoids, lats, glutes, quads, hamstrings, calves, …) exposed as
 * separate SVG paths. Any muscle can be recolored at runtime through the
 * `muscles` prop — no SVG editing needed.
 *
 * Props:
 *   gender:  'male' | 'female' | null     (null falls back to male)
 *   view:    'front' | 'back'
 *   muscles: { [slug]: 'light' | 'medium' | 'strong' }
 *
 * Slugs supported by the library (front + back combined):
 *   abs, adductors, ankles, biceps, calves, chest, deltoids, feet, forearm,
 *   gluteal, hamstring, hands, hair, head, knees, lower-back, neck,
 *   obliques, quadriceps, tibialis, trapezius, triceps, upper-back
 */

// colors[intensity - 1] = display color
// 'strong' -> 1 (most saturated), 'medium' -> 2, 'light' -> 3.
const INTENSITY_COLORS = ['#ef4444', '#fb923c', '#fbbf24']
const INTENSITY_BY_LEVEL = { strong: 1, medium: 2, light: 3 }

export default function BodyFigure({ gender = 'male', view = 'front', muscles = {} }) {
  const safeView = view === 'back' ? 'back' : 'front'

  const data = Object.entries(muscles)
    .filter(([, level]) => level && INTENSITY_BY_LEVEL[level])
    .map(([slug, level]) => ({ slug, intensity: INTENSITY_BY_LEVEL[level] }))

  return (
    <div className="anatomy-vector">
      <Body
        data={data}
        side={safeView}
        gender={gender === 'female' ? 'female' : 'male'}
        scale={1.1}
        colors={INTENSITY_COLORS}
        defaultFill="var(--muscle-base)"
        defaultStroke="var(--muscle-stroke)"
        defaultStrokeWidth={0.6}
        border="var(--muscle-stroke)"
      />
    </div>
  )
}
