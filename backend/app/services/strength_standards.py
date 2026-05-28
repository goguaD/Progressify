"""Strength-level classification based on 1RM relative to bodyweight.

Tier thresholds (bodyweight ratios) are aggregated from publicly published
strength standards (StrengthLevel.com / ExRx aggregated lifter data for
ages 20–40). For each exercise we store four cutoffs corresponding to the
minimum BW-ratio required to reach a tier:

    [novice, intermediate, advanced, elite]

A lifter whose ratio is below the *novice* threshold is classified as
``beginner``; the lowest tier is purposely lenient so untrained lifters
still receive feedback. The four levels exposed downstream map to the
``LEVELS`` constant used by the anatomy chart.
"""
from __future__ import annotations

# Standards in (male_thresholds, female_thresholds) keyed by exercise name
# exactly as stored on Exercise.name. Thresholds are bodyweight multipliers.
STRENGTH_STANDARDS: dict[str, dict[str, list[float]]] = {
    # ── Major compound lifts ────────────────────────────────────────────
    "Barbell Bench Press": {
        "male":   [0.75, 1.25, 1.75, 2.25],
        "female": [0.50, 0.75, 1.00, 1.40],
    },
    "Barbell Back Squat": {
        "male":   [1.00, 1.50, 2.25, 3.00],
        "female": [0.75, 1.25, 1.75, 2.25],
    },
    "Romanian Deadlift": {
        "male":   [1.10, 1.65, 2.25, 3.00],
        "female": [0.85, 1.30, 1.80, 2.30],
    },
    "Standing Overhead Press": {
        "male":   [0.50, 0.75, 1.25, 1.60],
        "female": [0.35, 0.55, 0.85, 1.15],
    },
    "Barbell Bent-Over Row": {
        "male":   [0.75, 1.25, 1.75, 2.25],
        "female": [0.50, 0.85, 1.25, 1.65],
    },
    "Pull-Ups": {
        # Total system load (bodyweight + extra weight).
        "male":   [1.00, 1.25, 1.60, 2.00],
        "female": [0.70, 0.90, 1.20, 1.55],
    },

    # ── Accessory presses / pulls ───────────────────────────────────────
    "Incline Dumbbell Press": {
        # Total load (both dumbbells combined).
        "male":   [0.55, 0.95, 1.35, 1.75],
        "female": [0.30, 0.55, 0.85, 1.15],
    },
    "Lat Pulldown": {
        "male":   [0.75, 1.10, 1.50, 1.90],
        "female": [0.50, 0.80, 1.10, 1.45],
    },
    "Seated Cable Row": {
        "male":   [0.75, 1.15, 1.55, 1.95],
        "female": [0.55, 0.85, 1.15, 1.55],
    },
    "Chest Dips": {
        # Total system load (bodyweight + extra).
        "male":   [1.00, 1.25, 1.55, 1.90],
        "female": [0.70, 0.95, 1.25, 1.55],
    },

    # ── Arms ────────────────────────────────────────────────────────────
    "Dumbbell Bicep Curl": {
        # Load on a single dumbbell.
        "male":   [0.25, 0.40, 0.55, 0.70],
        "female": [0.15, 0.25, 0.40, 0.55],
    },
    "Hammer Curl": {
        "male":   [0.25, 0.40, 0.55, 0.70],
        "female": [0.15, 0.25, 0.40, 0.55],
    },
    "Tricep Cable Pushdown": {
        "male":   [0.40, 0.65, 0.90, 1.15],
        "female": [0.25, 0.40, 0.60, 0.85],
    },
    "EZ-Bar Skull Crusher": {
        "male":   [0.40, 0.65, 0.90, 1.15],
        "female": [0.25, 0.40, 0.60, 0.85],
    },

    # ── Shoulders ───────────────────────────────────────────────────────
    "Dumbbell Lateral Raise": {
        "male":   [0.10, 0.18, 0.27, 0.40],
        "female": [0.05, 0.10, 0.18, 0.27],
    },
    "Reverse Pec Deck (Rear Delt Fly)": {
        "male":   [0.30, 0.55, 0.80, 1.05],
        "female": [0.20, 0.35, 0.55, 0.80],
    },
    "Face Pulls": {
        "male":   [0.30, 0.50, 0.70, 0.95],
        "female": [0.20, 0.35, 0.55, 0.75],
    },
    "Cable Chest Fly": {
        "male":   [0.30, 0.55, 0.80, 1.05],
        "female": [0.20, 0.35, 0.55, 0.80],
    },

    # ── Legs ────────────────────────────────────────────────────────────
    "Leg Press": {
        "male":   [1.75, 2.50, 3.25, 4.50],
        "female": [1.25, 1.85, 2.50, 3.25],
    },
    "Lying Leg Curl": {
        "male":   [0.50, 0.85, 1.25, 1.60],
        "female": [0.35, 0.55, 0.80, 1.10],
    },
    "Walking Lunges": {
        # Total dumbbell load.
        "male":   [0.50, 0.90, 1.30, 1.75],
        "female": [0.35, 0.65, 0.95, 1.30],
    },
    "Standing Calf Raise": {
        "male":   [1.50, 2.00, 2.50, 3.00],
        "female": [1.00, 1.50, 2.00, 2.50],
    },
}

# Tier names returned by the classifier.
LEVELS = ("beginner", "intermediate", "advanced", "elite")


# Plain-English instructions explaining what number the lifter should enter
# for each exercise. The frontend renders these directly under the input.
# Keys are exercise names exactly as stored on Exercise.name.
EXERCISE_UNIT_HINTS: dict[str, dict[str, str]] = {
    # ── Barbell movements: bar + plates total ───────────────────────────
    "Barbell Bench Press": {
        "en": "Total bar load (barbell + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (ღერძი + ბლინები), კგ-ში.",
    },
    "Barbell Back Squat": {
        "en": "Total bar load (barbell + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (ღერძი + ბლინები), კგ-ში.",
    },
    "Romanian Deadlift": {
        "en": "Total bar load (barbell + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (ღერძი + ბლინები), კგ-ში.",
    },
    "Standing Overhead Press": {
        "en": "Total bar load (barbell + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (ღერძი + ბლინები), კგ-ში.",
    },
    "Barbell Bent-Over Row": {
        "en": "Total bar load (barbell + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (ღერძი + ბლინები), კგ-ში.",
    },
    "EZ-Bar Skull Crusher": {
        "en": "Total bar load (EZ-bar + plates), in kg.",
        "ka": "ღერძის ჯამური წონა (EZ-ღერძი + ბლინები), კგ-ში.",
    },

    # ── Bodyweight + load movements: total system load ──────────────────
    "Pull-Ups": {
        "en": "Total system load (your bodyweight + any added weight). "
              "Leave blank if you cannot do a single rep.",
        "ka": "ჯამური დატვირთვა (თქვენი წონა + დამატებითი წონა). "
              "დატოვეთ ცარიელი, თუ ვერც ერთს ვერ აკეთებთ.",
    },
    "Chest Dips": {
        "en": "Total system load (your bodyweight + any added weight).",
        "ka": "ჯამური დატვირთვა (თქვენი წონა + დამატებითი წონა).",
    },

    # ── Two-dumbbell movements: combined load ──────────────────────────
    "Incline Dumbbell Press": {
        "en": "Combined load of both dumbbells (e.g. 30 kg + 30 kg = 60).",
        "ka": "ორივე გადასაწევის ჯამური წონა (მაგ. 30 + 30 = 60).",
    },
    "Walking Lunges": {
        "en": "Combined load of both dumbbells (e.g. 20 kg + 20 kg = 40).",
        "ka": "ორივე გადასაწევის ჯამური წონა.",
    },

    # ── Single-dumbbell isolation movements: per-hand load ──────────────
    "Dumbbell Bicep Curl": {
        "en": "Load on a single dumbbell (per hand), in kg.",
        "ka": "ერთი გადასაწევის წონა (თითო ხელზე), კგ-ში.",
    },
    "Hammer Curl": {
        "en": "Load on a single dumbbell (per hand), in kg.",
        "ka": "ერთი გადასაწევის წონა (თითო ხელზე), კგ-ში.",
    },
    "Dumbbell Lateral Raise": {
        "en": "Load on a single dumbbell (per hand), in kg.",
        "ka": "ერთი გადასაწევის წონა (თითო ხელზე), კგ-ში.",
    },

    # ── Cable / machine movements: selected stack weight ────────────────
    "Tricep Cable Pushdown": {
        "en": "Weight selected on the cable stack, in kg.",
        "ka": "კაბელის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Lat Pulldown": {
        "en": "Weight selected on the machine stack, in kg.",
        "ka": "ტრენაჟორის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Seated Cable Row": {
        "en": "Weight selected on the machine stack, in kg.",
        "ka": "ტრენაჟორის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Face Pulls": {
        "en": "Weight selected on the cable stack, in kg.",
        "ka": "კაბელის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Cable Chest Fly": {
        "en": "Combined weight per side, in kg (each pulley setting).",
        "ka": "თითო მხარის წონა ჯამში, კგ-ში.",
    },
    "Reverse Pec Deck (Rear Delt Fly)": {
        "en": "Weight selected on the machine stack, in kg.",
        "ka": "ტრენაჟორის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Leg Press": {
        "en": "Total weight loaded on the sled, in kg (excluding sled).",
        "ka": "სლედზე დატვირთული ჯამური წონა, კგ-ში.",
    },
    "Lying Leg Curl": {
        "en": "Weight selected on the machine stack, in kg.",
        "ka": "ტრენაჟორის სტეკზე არჩეული წონა, კგ-ში.",
    },
    "Standing Calf Raise": {
        "en": "Total load (machine plates or barbell), in kg.",
        "ka": "ჯამური დატვირთვა (ტრენაჟორი ან ღერძი), კგ-ში.",
    },

    # ── Bodyweight isolations: not weight-tracked ───────────────────────
    "Plank Hold": {
        "en": "Bodyweight exercise — leave blank or enter held time in seconds.",
        "ka": "სხეულის წონით სავარჯიშო — დატოვეთ ცარიელი ან ჩაწერეთ წამები.",
    },
    "Hanging Leg Raise": {
        "en": "Bodyweight exercise — leave blank if untracked.",
        "ka": "სხეულის წონით სავარჯიშო — დატოვეთ ცარიელი თუ არ ფასდება.",
    },
    "Cable Crunch": {
        "en": "Weight selected on the cable stack, in kg.",
        "ka": "კაბელის სტეკზე არჩეული წონა, კგ-ში.",
    },
}


def unit_hint(exercise_name: str, lang: str = "en") -> str | None:
    """Return the unit-entry hint for an exercise, or None if not mapped."""
    entry = EXERCISE_UNIT_HINTS.get(exercise_name)
    if not entry:
        return None
    return entry.get(lang) or entry.get("en")


def classify_lift(
    exercise_name: str,
    weight_kg: float,
    bodyweight_kg: float,
    gender: str,
) -> str | None:
    """Return the strength tier for a lift, or ``None`` if not enough info.

    The four tiers exposed to the rest of the app are:
        beginner < intermediate < advanced < elite

    Strength standards use five tiers internally (untrained, novice,
    intermediate, advanced, elite). Untrained and novice both collapse
    to ``beginner`` so the colour palette stays consistent with the
    anatomy chart.
    """
    if weight_kg <= 0 or bodyweight_kg <= 0:
        return None
    std = STRENGTH_STANDARDS.get(exercise_name)
    if std is None:
        return None
    table = std.get(gender if gender in std else "male")
    if not table:
        return None
    ratio = weight_kg / bodyweight_kg
    _novice, intermediate, advanced, elite = table
    if ratio >= elite:
        return "elite"
    if ratio >= advanced:
        return "advanced"
    if ratio >= intermediate:
        return "intermediate"
    # Anything below intermediate (including ``novice`` and ``untrained``)
    # is shown as beginner.
    return "beginner"


# Each exercise contributes to one or more muscle slugs. Mirrors the
# frontend's exerciseMuscles.js. Primary muscles get the full level,
# secondary muscles get one tier lower so the anatomy reflects the
# distinction visually.
EXERCISE_MUSCLES: dict[str, dict[str, list[str]]] = {
    "Barbell Bench Press":          {"primary": ["chest"],                  "secondary": ["triceps", "deltoids"]},
    "Incline Dumbbell Press":       {"primary": ["chest"],                  "secondary": ["deltoids", "triceps"]},
    "Chest Dips":                   {"primary": ["chest", "triceps"],       "secondary": ["deltoids"]},
    "Cable Chest Fly":              {"primary": ["chest"],                  "secondary": ["deltoids"]},
    "Pull-Ups":                     {"primary": ["upper-back"],             "secondary": ["biceps", "forearm"]},
    "Barbell Bent-Over Row":        {"primary": ["upper-back"],             "secondary": ["biceps", "lower-back", "trapezius"]},
    "Lat Pulldown":                 {"primary": ["upper-back"],             "secondary": ["biceps"]},
    "Seated Cable Row":             {"primary": ["upper-back"],             "secondary": ["biceps", "trapezius"]},
    "Face Pulls":                   {"primary": ["deltoids", "trapezius"],  "secondary": ["upper-back"]},
    "Standing Overhead Press":      {"primary": ["deltoids"],               "secondary": ["triceps", "trapezius"]},
    "Dumbbell Lateral Raise":       {"primary": ["deltoids"],               "secondary": ["trapezius"]},
    "Reverse Pec Deck (Rear Delt Fly)": {"primary": ["deltoids"],           "secondary": ["upper-back", "trapezius"]},
    "Dumbbell Bicep Curl":          {"primary": ["biceps"],                 "secondary": ["forearm"]},
    "Hammer Curl":                  {"primary": ["biceps"],                 "secondary": ["forearm"]},
    "Tricep Cable Pushdown":        {"primary": ["triceps"],                "secondary": []},
    "EZ-Bar Skull Crusher":         {"primary": ["triceps"],                "secondary": []},
    "Barbell Back Squat":           {"primary": ["quadriceps", "gluteal"],  "secondary": ["hamstring", "lower-back", "abs"]},
    "Romanian Deadlift":            {"primary": ["hamstring", "gluteal"],   "secondary": ["lower-back", "upper-back"]},
    "Leg Press":                    {"primary": ["quadriceps"],             "secondary": ["gluteal", "hamstring"]},
    "Lying Leg Curl":               {"primary": ["hamstring"],              "secondary": []},
    "Walking Lunges":               {"primary": ["quadriceps", "gluteal"],  "secondary": ["hamstring", "calves", "adductors"]},
    "Standing Calf Raise":          {"primary": ["calves"],                 "secondary": []},
    "Plank Hold":                   {"primary": ["abs"],                    "secondary": ["obliques"]},
    "Hanging Leg Raise":            {"primary": ["abs"],                    "secondary": ["obliques"]},
    "Cable Crunch":                 {"primary": ["abs"],                    "secondary": ["obliques"]},
}


_LEVEL_RANK = {"beginner": 0, "intermediate": 1, "advanced": 2, "elite": 3}
_RANK_LEVEL = {v: k for k, v in _LEVEL_RANK.items()}


def _max_level(a: str | None, b: str | None) -> str | None:
    if a is None:
        return b
    if b is None:
        return a
    return _RANK_LEVEL[max(_LEVEL_RANK[a], _LEVEL_RANK[b])]


def _step_down(level: str) -> str:
    """Drop a tier — used for secondary muscle contributions."""
    return _RANK_LEVEL[max(0, _LEVEL_RANK[level] - 1)]


def compute_muscle_levels(
    lifts: list[dict],
    bodyweight_kg: float | None,
    gender: str,
) -> dict[str, str]:
    """Aggregate per-exercise tiers into per-muscle tiers.

    ``lifts`` is an iterable of ``{"exercise_name": str, "weight_kg": float}``.
    For each lift we look up its primary and secondary muscles plus its
    strength tier and propagate the tier (one step lower for secondaries).
    A muscle's final tier is the highest tier it receives from any lift.
    """
    if not bodyweight_kg or bodyweight_kg <= 0:
        return {}

    muscles: dict[str, str | None] = {}
    for lift in lifts:
        name = lift.get("exercise_name")
        weight = lift.get("weight_kg")
        if not name or not weight:
            continue
        level = classify_lift(name, weight, bodyweight_kg, gender)
        if level is None:
            continue
        mapping = EXERCISE_MUSCLES.get(name)
        if not mapping:
            continue
        secondary_level = _step_down(level)
        for slug in mapping["primary"]:
            muscles[slug] = _max_level(muscles.get(slug), level)
        for slug in mapping["secondary"]:
            muscles[slug] = _max_level(muscles.get(slug), secondary_level)

    return {k: v for k, v in muscles.items() if v is not None}
