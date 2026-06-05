// Maps exercise name (English) → { primary, secondary } muscle slugs.
// Slugs match react-muscle-highlighter conventions used in AnatomySection.
//
// Primary  = muscles directly trained as the prime mover.
// Secondary = synergists / stabilisers that get noticeable work.

export const EXERCISE_MUSCLES = {
  // ── Chest ────────────────────────────────────────────────────────────
  'Barbell Bench Press': {
    primary: ['chest'],
    secondary: ['triceps', 'deltoids'],
  },
  'Incline Dumbbell Press': {
    primary: ['chest'],
    secondary: ['deltoids', 'triceps'],
  },
  'Chest Dips': {
    primary: ['chest', 'triceps'],
    secondary: ['deltoids'],
  },
  'Cable Chest Fly': {
    primary: ['chest'],
    secondary: ['deltoids'],
  },

  // ── Back ─────────────────────────────────────────────────────────────
  'Pull-Ups': {
    primary: ['upper-back'],
    secondary: ['biceps', 'forearm'],
  },
  'Barbell Bent-Over Row': {
    primary: ['upper-back'],
    secondary: ['biceps', 'lower-back', 'trapezius'],
  },
  'Lat Pulldown': {
    primary: ['upper-back'],
    secondary: ['biceps'],
  },
  'Seated Cable Row': {
    primary: ['upper-back'],
    secondary: ['biceps', 'trapezius'],
  },
  'Face Pulls': {
    primary: ['deltoids', 'trapezius'],
    secondary: ['upper-back'],
  },

  // ── Shoulders ────────────────────────────────────────────────────────
  'Standing Overhead Press': {
    primary: ['deltoids'],
    secondary: ['triceps', 'trapezius'],
  },
  'Dumbbell Lateral Raise': {
    primary: ['deltoids'],
    secondary: ['trapezius'],
  },
  'Reverse Pec Deck (Rear Delt Fly)': {
    primary: ['deltoids'],
    secondary: ['upper-back', 'trapezius'],
  },

  // ── Arms ─────────────────────────────────────────────────────────────
  'Dumbbell Bicep Curl': {
    primary: ['biceps'],
    secondary: ['forearm'],
  },
  'Hammer Curl': {
    primary: ['biceps'],
    secondary: ['forearm'],
  },
  'Tricep Cable Pushdown': {
    primary: ['triceps'],
    secondary: [],
  },
  'EZ-Bar Skull Crusher': {
    primary: ['triceps'],
    secondary: [],
  },

  // ── Legs ─────────────────────────────────────────────────────────────
  'Barbell Back Squat': {
    primary: ['quadriceps', 'gluteal'],
    secondary: ['hamstring', 'lower-back', 'abs'],
  },
  'Romanian Deadlift': {
    primary: ['hamstring', 'gluteal'],
    secondary: ['lower-back', 'upper-back'],
  },
  'Leg Press': {
    primary: ['quadriceps'],
    secondary: ['gluteal', 'hamstring'],
  },
  'Lying Leg Curl': {
    primary: ['hamstring'],
    secondary: [],
  },
  'Walking Lunges': {
    primary: ['quadriceps', 'gluteal'],
    secondary: ['hamstring', 'calves', 'adductors'],
  },
  'Standing Calf Raise': {
    primary: ['calves'],
    secondary: [],
  },

  // ── Core ─────────────────────────────────────────────────────────────
  'Plank Hold': {
    primary: ['abs'],
    secondary: ['obliques'],
  },
  'Hanging Leg Raise': {
    primary: ['abs'],
    secondary: ['obliques'],
  },
  'Cable Crunch': {
    primary: ['abs'],
    secondary: ['obliques'],
  },
}

// Fallback when exercise name isn't in the map: derive from muscle_group field.
// Maps the backend's muscle_group strings to slugs.
const MUSCLE_GROUP_TO_SLUG = {
  chest: 'chest',
  back: 'upper-back',
  shoulders: 'deltoids',
  biceps: 'biceps',
  triceps: 'triceps',
  quadriceps: 'quadriceps',
  hamstring: 'hamstring',
  calves: 'calves',
  abs: 'abs',
  glutes: 'gluteal',
  general: null,
}

export function musclesForExercise(exercise) {
  if (!exercise) return { primary: [], secondary: [] }
  const direct = EXERCISE_MUSCLES[exercise.name]
  if (direct) return direct
  const slug = MUSCLE_GROUP_TO_SLUG[exercise.muscle_group]
  return slug ? { primary: [slug], secondary: [] } : { primary: [], secondary: [] }
}
