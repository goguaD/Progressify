import Body from 'react-muscle-highlighter'

export const LEVELS = ['beginner', 'intermediate', 'advanced', 'elite']

export const LEVEL_COLORS = {
  beginner:     '#22c55e',
  intermediate: '#3b82f6',
  advanced:     '#a855f7',
  elite:        '#eab308',
}

const LEVEL_TO_INTENSITY = { beginner: 1, intermediate: 2, advanced: 3, elite: 4 }

export default function BodyFigure({ gender = 'male', view = 'front', muscles = {} }) {
  const safeView = view === 'back' ? 'back' : 'front'

  const data = Object.entries(muscles)
    .filter(([, level]) => level && LEVEL_TO_INTENSITY[level])
    .map(([slug, level]) => ({ slug, intensity: LEVEL_TO_INTENSITY[level] }))

  return (
    <div className="anatomy-vector">
      <Body
        data={data}
        side={safeView}
        gender={gender === 'female' ? 'female' : 'male'}
        scale={1.1}
        colors={[
          LEVEL_COLORS.beginner,
          LEVEL_COLORS.intermediate,
          LEVEL_COLORS.advanced,
          LEVEL_COLORS.elite,
        ]}
        defaultFill="var(--muscle-base)"
        defaultStroke="var(--muscle-stroke)"
        defaultStrokeWidth={0.6}
        border="var(--muscle-stroke)"
      />
    </div>
  )
}
