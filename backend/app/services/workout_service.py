"""Workout plan service: seed data and serialization helpers.

The rep-range to primary-purpose mapping is based on the ACSM/NSCA consensus
on resistance-training adaptations:

- 1–5 reps (≥85% 1RM, 3–5 min rest)  →  STRENGTH
- 6–12 reps (~67–85% 1RM, 1–2 min rest)  →  HYPERTROPHY (muscle growth)
- 13+ reps (<67% 1RM, 30–60 s rest)  →  MUSCULAR ENDURANCE
"""
import json

from app.models import Exercise, WorkoutDay, WorkoutPlan
from app.services.strength_standards import unit_hint


def _parse_muscle_targets(raw: str | None) -> list[dict]:
    """Decode the JSON ``muscle_targets`` column safely.

    Returns an empty list when missing or malformed so the API stays robust.
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except (ValueError, TypeError):
        return []
    if not isinstance(data, list):
        return []
    cleaned: list[dict] = []
    for item in data:
        if not isinstance(item, dict):
            continue
        slug = item.get("slug")
        intensity = item.get("intensity")
        if not slug or intensity not in {"low", "medium", "high"}:
            continue
        cleaned.append({"slug": str(slug), "intensity": intensity})
    return cleaned


def purpose_from_reps(rep_low: int, rep_high: int) -> str:
    """Map a rep range to its primary training adaptation."""
    mid = (rep_low + rep_high) / 2
    if mid <= 5:
        return "strength"
    if mid <= 12:
        return "hypertrophy"
    return "endurance"


def plan_summary_dict(
    plan: WorkoutPlan, my_rating: float | None = None,
) -> dict:
    rc = plan.rating_count or 0
    rs = plan.rating_sum or 0.0
    avg = round(rs / rc, 2) if rc > 0 else 0.0
    return {
        "id": plan.id,
        "name": plan.name,
        "name_ka": plan.name_ka,
        "description": plan.description,
        "description_ka": plan.description_ka,
        "image_url": plan.image_url,
        "days_per_week": plan.days_per_week,
        "split_type": plan.split_type,
        "level": plan.level,
        "views": plan.views,
        "rating": avg,
        "rating_count": rc,
        "my_rating": my_rating,
        "is_default": plan.is_default,
        "added_by": plan.added_by,
        "added_by_username": (
            plan.author.username
            if getattr(plan, "author", None) is not None
            else None
        ),
        "created_at": plan.created_at,
    }


def exercise_dict(ex: Exercise) -> dict:
    return {
        "id": ex.id,
        "order_index": ex.order_index,
        "name": ex.name,
        "name_ka": ex.name_ka,
        "description": ex.description,
        "description_ka": ex.description_ka,
        "image_url": ex.image_url,
        "sets": ex.sets,
        "rep_low": ex.rep_low,
        "rep_high": ex.rep_high,
        "rest_seconds": ex.rest_seconds,
        "primary_purpose": ex.primary_purpose,
        "muscle_group": ex.muscle_group,
        "muscle_targets": _parse_muscle_targets(
            ex.muscle_targets if ex.muscle_targets is None else str(ex.muscle_targets),
        ),
        "unit_hint": unit_hint(str(ex.name), "en"),
        "unit_hint_ka": unit_hint(str(ex.name), "ka"),
    }


def day_dict(day: WorkoutDay) -> dict:
    return {
        "id": day.id,
        "day_number": day.day_number,
        "name": day.name,
        "name_ka": day.name_ka,
        "focus": day.focus,
        "exercises": [exercise_dict(e) for e in day.exercises],
    }


def plan_detail_dict(
    plan: WorkoutPlan, my_rating: float | None = None,
) -> dict:
    base = plan_summary_dict(plan, my_rating)
    base["days"] = [day_dict(d) for d in plan.days]
    return base


# ─────────────────────────────────────────────────────────────────────────────
# EXERCISE LIBRARY
#
# Reusable exercise definitions to keep seed data DRY. Each entry contains the
# core movement info — description, image, muscle group. Sets/reps/rest are
# specified per use-case when added to a day.
# ─────────────────────────────────────────────────────────────────────────────

E = {
    # ── Chest ──────────────────────────────────────────────────────────────
    "bench_press": {
        "name": "Barbell Bench Press",
        "name_ka": "შტანგით ბენჩ პრესი",
        "muscle_group": "chest",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600",
        "description": (
            "Lie flat on a bench with feet planted. Grip the bar slightly wider than shoulder-width. "
            "Unrack the bar and lower it under control to mid-chest (touch lightly, do not bounce). "
            "Drive the bar up explosively while keeping shoulder blades retracted and pinned to the bench. "
            "Keep wrists stacked over elbows throughout."
        ),
        "description_ka": (
            "დაწექი ბენჩზე, ფეხები მყარად დადგი იატაკზე. დაიჭირე შტანგა მხრებზე ოდნავ "
            "ფართო ხელით. ჩამოწიე ნელა მკერდის შუა ნაწილამდე და სწრაფად ასწიე ზემოთ. "
            "ბეჭის ფრთები მთელი მოძრაობის განმავლობაში მოქცეული უნდა იყოს."
        ),
    },
    "incline_db_press": {
        "name": "Incline Dumbbell Press",
        "name_ka": "ინკლაინ წონებით პრესი",
        "muscle_group": "chest",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "description": (
            "Set the bench to a 30° incline. Hold a dumbbell in each hand at chest level with palms forward. "
            "Press the dumbbells up and slightly inward until your arms are nearly straight (do not lock out). "
            "Lower under control to a deep stretch at chest level. This emphasises the upper chest fibers."
        ),
        "description_ka": (
            "მოაწესრიგე ბენჩი 30°-ზე. დაიჭირე წონები მკერდის სიმაღლეზე, ხელისგულები წინ. "
            "ასწიე ზემოთ და ოდნავ შიგნით სანამ მკლავები არ გაიშლება. დაუბრუნე ნელა."
        ),
    },
    "chest_dips": {
        "name": "Chest Dips",
        "name_ka": "მკერდის დიფსები",
        "muscle_group": "chest",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "description": (
            "Grip parallel dip bars and support yourself with arms straight. Lean your torso forward 30° "
            "and lower yourself by bending the elbows until your shoulders sit just below your elbows. "
            "Drive back up by pushing through the palms. Forward lean targets the chest; upright targets triceps."
        ),
        "description_ka": (
            "დაიჭირე პარალელური ჩხირები გასწორებული მკლავებით. დახარე ტანი 30°-ით წინ "
            "და დაიწიე სანამ მხრები არ ჩავა იდაყვებზე ქვემოთ. ასწიე უკან საწყის პოზიციაში."
        ),
    },
    "cable_fly": {
        "name": "Cable Chest Fly",
        "name_ka": "ბროყნზე მკერდის ფლაი",
        "muscle_group": "chest",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
        "description": (
            "Set both cables to upper-chest height. Grasp a handle in each hand and step forward into a "
            "staggered stance. With a slight bend in the elbows, draw both hands together in front of your chest "
            "in a wide arc, squeezing for one second at the bottom. Return slowly under control."
        ),
        "description_ka": (
            "მოაწესრიგე ბროყნი მკერდის ზედა დონეზე. დაიჭირე სახელურები ორივე ხელით, "
            "გადადგი ერთი ფეხი წინ. შემოიკრიბე ხელები მკერდის წინ ფართო რკალით, "
            "შეიკუმშე 1 წამი. დაუბრუნე ნელა."
        ),
    },

    # ── Back ───────────────────────────────────────────────────────────────
    "pull_ups": {
        "name": "Pull-Ups",
        "name_ka": "გადაცემები (Pull-Ups)",
        "muscle_group": "back",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=600",
        "description": (
            "Hang from a pull-up bar with an overhand grip slightly wider than shoulder-width. "
            "Pull your elbows down and back, driving them toward your hips, until your chin clears the bar. "
            "Lower yourself with control over 2–3 seconds. Use a band for assistance if needed."
        ),
        "description_ka": (
            "ჩამოეკიდე ჩხირზე ხელისგულებით წინ მიმართული, მხრებზე ოდნავ ფართო. "
            "ასწიე თავი იდაყვების ქვემოთ ჩამოწევით, სანამ ნიკაპი არ გადასცდება ჩხირს. "
            "ჩამოდი ნელა 2–3 წამში."
        ),
    },
    "barbell_row": {
        "name": "Barbell Bent-Over Row",
        "name_ka": "შტანგით წელის როუ",
        "muscle_group": "back",
        "image_url": "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=600",
        "description": (
            "Stand with feet hip-width. Hinge at the hips with a flat back until your torso is around 45° "
            "to the floor. Hold the bar with an overhand grip just outside your knees. Pull the bar to your "
            "lower ribcage by driving the elbows back. Squeeze the shoulder blades together at the top."
        ),
        "description_ka": (
            "დადექი ფეხებით მენჯის სიგანეზე. დახარე ტანი თეძოებიდან 45°-მდე, ზურგი ბრტყელი. "
            "დაიჭირე შტანგა მუხლების გვერდით. მიართვი მუცლის ქვედა ნეკნებამდე იდაყვების უკან წევით."
        ),
    },
    "lat_pulldown": {
        "name": "Lat Pulldown",
        "name_ka": "ვერტიკალური ტრექი (Lat Pulldown)",
        "muscle_group": "back",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "description": (
            "Sit with thighs locked under the pads. Grip the bar slightly wider than shoulder-width with palms forward. "
            "Lean back 10–15° and pull the bar to your upper chest, driving elbows down and back. "
            "Control the bar back up over 2 seconds to a full stretch."
        ),
        "description_ka": (
            "ჩამოჯექი ბარძაყები ბალიშების ქვეშ. დაიჭირე ჩხირი მხრებზე ფართო ხელისგულებით წინ. "
            "ოდნავ დახარე უკან და ჩამოწიე ჩხირი მკერდის ზედა ნაწილამდე."
        ),
    },
    "seated_row": {
        "name": "Seated Cable Row",
        "name_ka": "ჩამოჯდომით ბროყნზე როუ",
        "muscle_group": "back",
        "image_url": "https://images.unsplash.com/photo-1517344800994-80b20d05bb9d?w=600",
        "description": (
            "Sit at the cable row machine with feet braced and knees slightly bent. Grip the handle, keep your "
            "torso upright, and pull the handle to your lower belly by driving elbows straight back. "
            "Squeeze the mid-back for 1 second, then extend the arms slowly while keeping the chest tall."
        ),
        "description_ka": (
            "ჩამოჯექი, ფეხები მყარად ბრძოლის ფარზე. დაიჭირე სახელური, ტანი სწორი. "
            "მიართვი მუცლის ქვედა ნაწილამდე იდაყვების უკან წევით. შეიკუმშე 1 წამი."
        ),
    },
    "face_pulls": {
        "name": "Face Pulls",
        "name_ka": "სახეზე გადაცემები",
        "muscle_group": "back",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
        "description": (
            "Set a rope attachment to slightly above eye-level. Grip the rope with both hands, palms facing in. "
            "Pull the rope toward your forehead, separating your hands as the elbows flare high and out. "
            "Hold the contraction with shoulder blades pinched, then return slowly. Excellent for rear delts & posture."
        ),
        "description_ka": (
            "მოაწესრიგე თოკი თვალის დონეზე ოდნავ მაღლა. დაიჭირე ორივე ხელით. "
            "მიართვი თოკი შუბლისკენ, იდაყვები მაღლა და გვერდებზე. შეიკუმშე და დაუბრუნე."
        ),
    },

    # ── Shoulders ──────────────────────────────────────────────────────────
    "overhead_press": {
        "name": "Standing Overhead Press",
        "name_ka": "თავზე გადასაცემი (Overhead Press)",
        "muscle_group": "shoulders",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600",
        "description": (
            "Stand with feet hip-width and hold the bar at the front of your shoulders with elbows under the bar. "
            "Brace your core and squeeze your glutes. Press the bar straight overhead, moving your head slightly "
            "forward as the bar passes your face. Lock out with arms straight, bar over mid-foot."
        ),
        "description_ka": (
            "დადექი ფეხებით მენჯის სიგანეზე, შტანგა მხრების წინ, იდაყვები შტანგის ქვემოთ. "
            "ააწიე შტანგა პირდაპირ თავზე. სახე გადაიწიე ოდნავ წინ შტანგის გადასასვლელად."
        ),
    },
    "lateral_raise": {
        "name": "Dumbbell Lateral Raise",
        "name_ka": "გვერდითი წონების აწევა",
        "muscle_group": "shoulders",
        "image_url": "https://images.unsplash.com/photo-1581009137042-c552e485697a?w=600",
        "description": (
            "Stand with a dumbbell in each hand at your sides, palms facing in. With a soft bend in the elbows, "
            "raise the dumbbells out to your sides until your arms are roughly parallel to the floor. "
            "Lead with the elbows, not the hands. Lower slowly over 2–3 seconds. Use lighter weights and strict form."
        ),
        "description_ka": (
            "დადექი წონებით ხელში გვერდებზე. იდაყვების ოდნავ მოხრით ასწიე გვერდებზე "
            "სანამ მკლავები პარალელური არ გახდება იატაკთან. დაუბრუნე ნელა."
        ),
    },
    "rear_delt_fly": {
        "name": "Reverse Pec Deck (Rear Delt Fly)",
        "name_ka": "უკანა დელტოიდის ფლაი",
        "muscle_group": "shoulders",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
        "description": (
            "Set the pec deck to reverse-fly position and sit facing the pad. Grip the handles with arms extended in "
            "front of you. Squeeze your shoulder blades together as you draw your arms back and out in a wide arc "
            "until your elbows align with your shoulders. Hold for 1 second."
        ),
        "description_ka": (
            "მოაწესრიგე პეკ-დეკი უკუ-ფლაი პოზიციაში. დაიჭირე სახელურები წინ გაშლილი ხელებით. "
            "გადასწიე უკან ბეჭის ფრთების შეკუმშვით სანამ იდაყვები მხრებთან არ გასწორდება."
        ),
    },

    # ── Arms ───────────────────────────────────────────────────────────────
    "bicep_curl": {
        "name": "Dumbbell Bicep Curl",
        "name_ka": "ბიცეფსის წონებით კერლი",
        "muscle_group": "biceps",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "description": (
            "Stand with a dumbbell in each hand, palms facing forward, elbows pinned to your sides. "
            "Curl the dumbbells up by flexing the biceps until your forearms are vertical. Squeeze at the top, "
            "then lower over 2 seconds. Keep elbows locked in place — do not swing the body."
        ),
        "description_ka": (
            "დადექი წონებით ხელში, ხელისგულები წინ, იდაყვები გვერდებთან. "
            "ააწიე წონები ბიცეფსის შეკუმშვით სანამ წინამხრები ვერტიკალური არ გახდება."
        ),
    },
    "hammer_curl": {
        "name": "Hammer Curl",
        "name_ka": "ჩაქუჩისებრი კერლი",
        "muscle_group": "biceps",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "description": (
            "Same as a dumbbell curl but with palms facing each other throughout the lift (a neutral grip). "
            "Curl both dumbbells together with elbows pinned. This emphasises the brachialis and forearm flexors "
            "for thicker-looking arms."
        ),
        "description_ka": (
            "იგივე რაც ჩვეულებრივი კერლი, ოღონდ ხელისგულები ერთმანეთს უყურებენ. "
            "ააწიე ორივე წონა ერთად — აზარდებს ბრაქიალისს და წინამხარს."
        ),
    },
    "tricep_pushdown": {
        "name": "Tricep Cable Pushdown",
        "name_ka": "ტრიცეფსის პუშდაუნი",
        "muscle_group": "triceps",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "description": (
            "Stand at a cable station with a straight or v-bar attachment at chest height. Grip the bar with palms down "
            "and pin your elbows to your sides. Press the bar down by extending your elbows fully — your upper arms "
            "must stay still. Squeeze the triceps hard at lock-out, then return slowly."
        ),
        "description_ka": (
            "დადექი ბროყნის სადგართან. დაიჭირე ჩხირი ხელისგულებით ქვემოთ, იდაყვები გვერდებთან. "
            "ჩაწიე ჩხირი ქვემოთ იდაყვების სრული გაშლით."
        ),
    },
    "skull_crusher": {
        "name": "EZ-Bar Skull Crusher",
        "name_ka": "EZ-შტანგით სკალ ქრაშერი",
        "muscle_group": "triceps",
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600",
        "description": (
            "Lie on a bench holding an EZ-bar with a close grip. Press the bar to lockout above your chest. "
            "Keeping the upper arms still and elbows pointing at the ceiling, bend the elbows to lower the bar "
            "toward your forehead. Reverse the motion to lockout. Move slowly to protect the elbows."
        ),
        "description_ka": (
            "დაწექი ბენჩზე, დაიჭირე EZ-შტანგა ვიწრო ხელით. ააწიე მკერდის თავზე. "
            "მკლავები ვერტიკალურად, იდაყვების მოხრით ჩაუშვი შტანგა შუბლისკენ, შემდეგ ააწიე უკან."
        ),
    },

    # ── Legs ───────────────────────────────────────────────────────────────
    "back_squat": {
        "name": "Barbell Back Squat",
        "name_ka": "ზურგზე შტანგით სქვაჯი",
        "muscle_group": "quadriceps",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=600",
        "description": (
            "Set the bar on a rack at chest height. Step under and place the bar on your upper-back traps (high-bar) "
            "or rear delts (low-bar). Brace your core, unrack, and step back. Squat down by pushing your hips back and "
            "bending the knees until thighs are at least parallel to the floor. Drive up through the mid-foot."
        ),
        "description_ka": (
            "მოაწესრიგე შტანგა მკერდის სიმაღლეზე. დადგი მხრებზე. შემოატრიალე ბირთვი, ჩამოდი. "
            "მენჯი უკან წაიწიე და მუხლების მოხრით ჩაჯექი ბარძაყები პარალელურამდე. ააწიე ფეხის შუა ნაწილით."
        ),
    },
    "romanian_deadlift": {
        "name": "Romanian Deadlift",
        "name_ka": "რუმინული დედლიფტი",
        "muscle_group": "hamstring",
        "image_url": "https://images.unsplash.com/photo-1517344800994-80b20d05bb9d?w=600",
        "description": (
            "Stand with the bar in front of your thighs, feet hip-width, soft knees. Hinge at the hips by pushing your "
            "butt back as you slide the bar down your thighs. Keep the bar in contact with your legs and your back flat. "
            "Stop when you feel a deep stretch in the hamstrings, then drive the hips forward to stand up."
        ),
        "description_ka": (
            "დადექი შტანგით ბარძაყების წინ, ფეხები მენჯის სიგანეზე, მუხლები ოდნავ მოხრილი. "
            "მენჯი წაიწიე უკან შტანგის ფეხებზე ჩასრიალებით სანამ ჰამსტრინგზე გაჭიმვა არ იგრძნო."
        ),
    },
    "leg_press": {
        "name": "Leg Press",
        "name_ka": "ფეხის პრესი",
        "muscle_group": "quadriceps",
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "description": (
            "Sit in the leg press machine with feet shoulder-width on the platform. Unlock the safety and lower the "
            "platform under control until your knees are at 90° (don't let your lower back round off the pad). "
            "Push back up powerfully without locking the knees. Foot placement higher emphasises glutes/hams."
        ),
        "description_ka": (
            "ჩამოჯექი ლეგ პრესის მანქანაში, ფეხები მხრების სიგანეზე. ჩაუშვი პლატფორმა მუხლების 90°-მდე. "
            "ააწიე უკან მუხლების სრული გაშლის გარეშე."
        ),
    },
    "leg_curl": {
        "name": "Lying Leg Curl",
        "name_ka": "ჰამსტრინგის კერლი (ლეგ კერლი)",
        "muscle_group": "hamstring",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
        "description": (
            "Lie face down on the leg curl machine with the pad just above your heels. Grip the handles. "
            "Curl your heels toward your glutes by flexing the hamstrings. Hold the peak contraction for 1 second, "
            "then lower over 2–3 seconds to a full stretch. Keep the hips pressed to the bench."
        ),
        "description_ka": (
            "დაწექი ლეგ კერლის მანქანაზე, ბალიში ქუსლების ზემოთ. "
            "მოხარე ფეხები საფასურისკენ ჰამსტრინგის შეკუმშვით. დაუბრუნე ნელა."
        ),
    },
    "walking_lunge": {
        "name": "Walking Lunges",
        "name_ka": "ნაბიჯ-ნაბიჯ ლანჯები",
        "muscle_group": "quadriceps",
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=600",
        "description": (
            "Hold a dumbbell in each hand or rest a barbell across your upper back. Step forward into a lunge so the "
            "front thigh is parallel to the floor and the back knee hovers just above it. Drive through the front heel "
            "to step the back foot through into the next lunge."
        ),
        "description_ka": (
            "დაიჭირე წონები ან შტანგა ზურგზე. გადადგი წინ — წინა ბარძაყი იატაკის პარალელური, "
            "უკანა მუხლი იატაკის თავზე. ააწიე უკანა ფეხი წინ შემდეგი ნაბიჯისთვის."
        ),
    },
    "calf_raise": {
        "name": "Standing Calf Raise",
        "name_ka": "ფეხის წვერებზე აწევა",
        "muscle_group": "calves",
        "image_url": "https://images.unsplash.com/photo-1517344800994-80b20d05bb9d?w=600",
        "description": (
            "Stand on a calf-raise block or the edge of a step with the balls of your feet, heels hanging off. "
            "Drop your heels below the platform for a full stretch, then press up onto the balls of your feet as "
            "high as possible. Pause at the top for 1 second. Move slowly — calves respond best to controlled tempo."
        ),
        "description_ka": (
            "დადექი კიბის კიდეზე ფეხის წვერებით, ქუსლები ჰაერში. "
            "ჩამოუშვი ქუსლები გასაჭიმად, შემდეგ ააწიე მაქსიმალურად მაღლა. შეიკუმშე 1 წამი."
        ),
    },

    # ── Core ───────────────────────────────────────────────────────────────
    "plank": {
        "name": "Plank Hold",
        "name_ka": "პლანკის გაჩერება",
        "muscle_group": "abs",
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "description": (
            "Get into a forearm plank: elbows under shoulders, feet hip-width, body in a straight line from head to "
            "heels. Squeeze your glutes, brace your abs hard, and tuck your pelvis slightly under. Breathe steadily. "
            "Drop the hips or arch your back and the set is over."
        ),
        "description_ka": (
            "დადექი წინამხრების პლანკში: იდაყვები მხრების ქვემოთ, ფეხები მენჯის სიგანეზე. "
            "სხეული სწორი ხაზი თავიდან ქუსლებამდე. შეიკუმშე საფასური და მუცელი."
        ),
    },
    "hanging_leg_raise": {
        "name": "Hanging Leg Raise",
        "name_ka": "ჩამოკიდებული ფეხების აწევა",
        "muscle_group": "abs",
        "image_url": "https://images.unsplash.com/photo-1598971639058-fab3c3109a00?w=600",
        "description": (
            "Hang from a pull-up bar with a firm grip and slight bend in the elbows. Keeping your legs together, "
            "raise them under control until your thighs are parallel to the floor (or higher for advanced). "
            "Do not swing — initiate the movement by tucking the pelvis. Lower slowly over 2–3 seconds."
        ),
        "description_ka": (
            "ჩამოეკიდე ჩხირზე, იდაყვები ოდნავ მოხრილი. ფეხები ერთად, ააწიე ნელა "
            "სანამ ბარძაყები იატაკის პარალელური არ გახდება. დაუბრუნე ნელა."
        ),
    },
    "cable_crunch": {
        "name": "Cable Crunch",
        "name_ka": "ბროყნზე ქრანჩი",
        "muscle_group": "abs",
        "image_url": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=600",
        "description": (
            "Kneel facing a cable station with a rope attached high. Hold the rope by your forehead. Initiate the "
            "movement by curling your spine — bring your elbows toward your knees. Do NOT pull with the arms or hinge "
            "at the hips. Squeeze the abs hard at the bottom."
        ),
        "description_ka": (
            "ჩაიჩოქე ბროყნისკენ თოკი მაღლა. დაიჭირე თოკი შუბლთან. ხერხემლის მოხრით "
            "მიართვი იდაყვები მუხლებთან — არ გაამოძრავო მენჯი."
        ),
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# PLAN DEFINITIONS
# Each plan provides days, and each day is a list of (exercise_key, sets, reps,
# rest_seconds) tuples. The reps field can be "8-12" or a single number.
# ─────────────────────────────────────────────────────────────────────────────


def _parse_reps(reps: str | int) -> tuple[int, int]:
    if isinstance(reps, int):
        return reps, reps
    if "-" in reps:
        lo, hi = reps.split("-", 1)
        return int(lo.strip()), int(hi.strip())
    return int(reps), int(reps)


DEFAULT_PLANS: list[dict] = [
    # ─── 3-DAY PLANS ──────────────────────────────────────────────────────
    {
        "name": "Full Body 3x/Week",
        "name_ka": "სრული სხეული 3-ჯერ კვირაში",
        "description": (
            "A balanced 3-day full-body routine ideal for beginners and busy intermediates. "
            "Each session targets every major muscle group with one heavy compound and accessories. "
            "Train with 48 hours rest between sessions (e.g. Mon/Wed/Fri)."
        ),
        "description_ka": (
            "დაბალანსებული 3-დღიანი სრული სხეულის რუტინა, შესაფერისი დამწყებთათვის და დაკავებული საშუალო დონის "
            "მოვარჯიშეთათვის. თითოეული სესია მოიცავს ყველა მთავარ კუნთს. 48 საათი დასვენება სესიებს შორის."
        ),
        "image_url": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=600",
        "days_per_week": 3,
        "split_type": "full_body",
        "level": "beginner",
        "days": [
            {
                "name": "Day A — Squat Focus",
                "name_ka": "დღე A — სქვაჯის ფოკუსი",
                "focus": "quads, chest, back",
                "exercises": [
                    ("back_squat", 4, "5-8", 180),
                    ("bench_press", 3, "6-10", 120),
                    ("barbell_row", 3, "6-10", 120),
                    ("lateral_raise", 3, "12-15", 60),
                    ("plank", 3, "30-60", 60),
                ],
            },
            {
                "name": "Day B — Hinge Focus",
                "name_ka": "დღე B — დედლიფტის ფოკუსი",
                "focus": "hamstrings, back, shoulders",
                "exercises": [
                    ("romanian_deadlift", 4, "5-8", 180),
                    ("overhead_press", 3, "6-10", 120),
                    ("lat_pulldown", 3, "8-12", 90),
                    ("bicep_curl", 3, "10-12", 60),
                    ("calf_raise", 3, "12-15", 60),
                ],
            },
            {
                "name": "Day C — Volume Day",
                "name_ka": "დღე C — მოცულობის დღე",
                "focus": "full body, hypertrophy",
                "exercises": [
                    ("leg_press", 3, "10-12", 120),
                    ("incline_db_press", 3, "8-12", 90),
                    ("seated_row", 3, "8-12", 90),
                    ("tricep_pushdown", 3, "10-12", 60),
                    ("hammer_curl", 3, "10-12", 60),
                    ("hanging_leg_raise", 3, "8-12", 60),
                ],
            },
        ],
    },
    {
        "name": "Push / Pull / Legs (3-Day)",
        "name_ka": "Push / Pull / Legs (3-დღიანი)",
        "description": (
            "The classic PPL split run once per week — pushing muscles (chest, shoulders, triceps) on Day 1, "
            "pulling muscles (back, biceps) on Day 2, and legs on Day 3. Allows full recovery between sessions "
            "while hitting each muscle group with focused volume."
        ),
        "description_ka": (
            "კლასიკური PPL სპლიტი კვირაში ერთხელ — დღე 1 ბიძგი (მკერდი, მხრები, ტრიცეფსი), "
            "დღე 2 გაწევა (ზურგი, ბიცეფსი), დღე 3 ფეხები. სრული აღდგენა სესიებს შორის."
        ),
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "days_per_week": 3,
        "split_type": "ppl",
        "level": "intermediate",
        "days": [
            {
                "name": "Push Day",
                "name_ka": "ბიძგის დღე",
                "focus": "chest, shoulders, triceps",
                "exercises": [
                    ("bench_press", 4, "6-8", 180),
                    ("overhead_press", 3, "6-10", 120),
                    ("incline_db_press", 3, "8-12", 90),
                    ("lateral_raise", 4, "12-15", 60),
                    ("tricep_pushdown", 3, "10-12", 60),
                    ("skull_crusher", 3, "8-12", 60),
                ],
            },
            {
                "name": "Pull Day",
                "name_ka": "გაწევის დღე",
                "focus": "back, biceps, rear delts",
                "exercises": [
                    ("barbell_row", 4, "6-8", 180),
                    ("pull_ups", 3, "6-10", 120),
                    ("lat_pulldown", 3, "8-12", 90),
                    ("face_pulls", 3, "12-15", 60),
                    ("bicep_curl", 3, "10-12", 60),
                    ("hammer_curl", 3, "10-12", 60),
                ],
            },
            {
                "name": "Leg Day",
                "name_ka": "ფეხების დღე",
                "focus": "quads, hamstrings, glutes, calves",
                "exercises": [
                    ("back_squat", 4, "5-8", 180),
                    ("romanian_deadlift", 3, "6-10", 150),
                    ("leg_press", 3, "10-12", 120),
                    ("walking_lunge", 3, "10-12", 90),
                    ("leg_curl", 3, "10-12", 60),
                    ("calf_raise", 4, "12-15", 60),
                ],
            },
        ],
    },

    # ─── 4-DAY PLANS ──────────────────────────────────────────────────────
    {
        "name": "Upper / Lower Split (4-Day)",
        "name_ka": "ზედა / ქვედა სპლიტი (4-დღიანი)",
        "description": (
            "A 4-day upper/lower split — two upper-body days and two lower-body days per week. "
            "Each muscle group is hit twice per week, which research consistently shows is optimal for hypertrophy. "
            "Schedule: Mon (Upper), Tue (Lower), Thu (Upper), Fri (Lower)."
        ),
        "description_ka": (
            "4-დღიანი ზედა/ქვედა სპლიტი — ორი ზედა-სხეულის და ორი ქვედა-სხეულის დღე კვირაში. "
            "თითოეული კუნთი ვარჯიშდება ორჯერ კვირაში, რაც კვლევებით ოპტიმალურია ჰიპერტროფიისთვის."
        ),
        "image_url": "https://images.unsplash.com/photo-1574680096145-d05b474e2155?w=600",
        "days_per_week": 4,
        "split_type": "upper_lower",
        "level": "intermediate",
        "days": [
            {
                "name": "Upper A — Strength",
                "name_ka": "ზედა A — ძალა",
                "focus": "chest, back (heavy)",
                "exercises": [
                    ("bench_press", 5, "4-6", 180),
                    ("barbell_row", 5, "4-6", 180),
                    ("overhead_press", 3, "6-8", 120),
                    ("pull_ups", 3, "6-10", 120),
                    ("tricep_pushdown", 3, "8-12", 60),
                    ("bicep_curl", 3, "8-12", 60),
                ],
            },
            {
                "name": "Lower A — Strength",
                "name_ka": "ქვედა A — ძალა",
                "focus": "quads, hamstrings (heavy)",
                "exercises": [
                    ("back_squat", 5, "4-6", 180),
                    ("romanian_deadlift", 4, "6-8", 150),
                    ("walking_lunge", 3, "8-10", 90),
                    ("leg_curl", 3, "8-12", 60),
                    ("calf_raise", 4, "10-15", 60),
                    ("plank", 3, "45-60", 60),
                ],
            },
            {
                "name": "Upper B — Hypertrophy",
                "name_ka": "ზედა B — ჰიპერტროფია",
                "focus": "chest, back, arms (volume)",
                "exercises": [
                    ("incline_db_press", 4, "8-12", 90),
                    ("seated_row", 4, "8-12", 90),
                    ("lat_pulldown", 3, "10-12", 90),
                    ("cable_fly", 3, "12-15", 60),
                    ("lateral_raise", 4, "12-15", 60),
                    ("hammer_curl", 3, "10-12", 60),
                    ("skull_crusher", 3, "10-12", 60),
                ],
            },
            {
                "name": "Lower B — Hypertrophy",
                "name_ka": "ქვედა B — ჰიპერტროფია",
                "focus": "legs (volume)",
                "exercises": [
                    ("leg_press", 4, "10-12", 120),
                    ("walking_lunge", 3, "10-12", 90),
                    ("leg_curl", 4, "10-15", 60),
                    ("calf_raise", 4, "12-20", 60),
                    ("hanging_leg_raise", 3, "10-15", 60),
                    ("cable_crunch", 3, "12-15", 60),
                ],
            },
        ],
    },
    {
        "name": "Push / Pull / Legs / Upper (4-Day)",
        "name_ka": "Push / Pull / Legs / Upper (4-დღიანი)",
        "description": (
            "A hybrid PPL+Upper combo for those wanting extra upper-body work. Run PPL on three days and add an "
            "extra upper-body session for chest, back, and arms with high volume. Schedule: Mon/Tue/Thu/Fri."
        ),
        "description_ka": (
            "ჰიბრიდული PPL+Upper სქემა, ვინც ზედა სხეულზე მეტ ვარჯიშს ეძებს. PPL სამი დღე "
            "და დამატებითი ზედა სხეულის სესია."
        ),
        "image_url": "https://images.unsplash.com/photo-1581009146145-b5ef050c2e1e?w=600",
        "days_per_week": 4,
        "split_type": "ppl_upper",
        "level": "intermediate",
        "days": [
            {
                "name": "Push Day",
                "name_ka": "ბიძგის დღე",
                "focus": "chest, shoulders, triceps",
                "exercises": [
                    ("bench_press", 4, "6-8", 180),
                    ("overhead_press", 3, "6-10", 120),
                    ("incline_db_press", 3, "8-12", 90),
                    ("lateral_raise", 4, "12-15", 60),
                    ("tricep_pushdown", 3, "10-12", 60),
                ],
            },
            {
                "name": "Pull Day",
                "name_ka": "გაწევის დღე",
                "focus": "back, biceps",
                "exercises": [
                    ("barbell_row", 4, "6-8", 180),
                    ("pull_ups", 3, "6-10", 120),
                    ("lat_pulldown", 3, "8-12", 90),
                    ("face_pulls", 3, "12-15", 60),
                    ("bicep_curl", 4, "10-12", 60),
                ],
            },
            {
                "name": "Leg Day",
                "name_ka": "ფეხების დღე",
                "focus": "quads, hamstrings, calves",
                "exercises": [
                    ("back_squat", 4, "5-8", 180),
                    ("romanian_deadlift", 3, "6-10", 150),
                    ("leg_press", 3, "10-12", 120),
                    ("leg_curl", 3, "10-12", 60),
                    ("calf_raise", 4, "12-15", 60),
                ],
            },
            {
                "name": "Upper Volume",
                "name_ka": "ზედა მოცულობა",
                "focus": "chest, back, arms (volume)",
                "exercises": [
                    ("incline_db_press", 4, "10-12", 90),
                    ("seated_row", 4, "10-12", 90),
                    ("cable_fly", 3, "12-15", 60),
                    ("rear_delt_fly", 3, "12-15", 60),
                    ("hammer_curl", 3, "10-12", 60),
                    ("skull_crusher", 3, "10-12", 60),
                ],
            },
        ],
    },

    # ─── 5-DAY PLANS ──────────────────────────────────────────────────────
    {
        "name": "Bro Split (5-Day)",
        "name_ka": "Bro სპლიტი (5-დღიანი)",
        "description": (
            "The classic bodybuilder 5-day split — one muscle group per session with high volume. "
            "Excellent for advanced lifters who can recover from focused volume. Mon: Chest, Tue: Back, "
            "Wed: Shoulders, Thu: Arms, Fri: Legs."
        ),
        "description_ka": (
            "კლასიკური ბოდიბილდინგ 5-დღიანი სპლიტი — ერთი კუნთის ჯგუფი თითო სესიაში. "
            "შესაფერისი მოწინავე მოვარჯიშეთათვის."
        ),
        "image_url": "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=600",
        "days_per_week": 5,
        "split_type": "bro_split",
        "level": "advanced",
        "days": [
            {
                "name": "Chest Day",
                "name_ka": "მკერდის დღე",
                "focus": "chest, triceps secondary",
                "exercises": [
                    ("bench_press", 4, "6-8", 180),
                    ("incline_db_press", 4, "8-12", 90),
                    ("chest_dips", 3, "8-12", 90),
                    ("cable_fly", 4, "12-15", 60),
                    ("tricep_pushdown", 3, "10-12", 60),
                ],
            },
            {
                "name": "Back Day",
                "name_ka": "ზურგის დღე",
                "focus": "back, biceps secondary",
                "exercises": [
                    ("pull_ups", 4, "6-10", 120),
                    ("barbell_row", 4, "6-10", 150),
                    ("lat_pulldown", 3, "8-12", 90),
                    ("seated_row", 3, "10-12", 90),
                    ("face_pulls", 3, "12-15", 60),
                ],
            },
            {
                "name": "Shoulder Day",
                "name_ka": "მხრების დღე",
                "focus": "shoulders, traps",
                "exercises": [
                    ("overhead_press", 4, "6-8", 150),
                    ("lateral_raise", 5, "12-15", 60),
                    ("rear_delt_fly", 4, "12-15", 60),
                    ("face_pulls", 3, "15-20", 45),
                ],
            },
            {
                "name": "Arm Day",
                "name_ka": "მკლავების დღე",
                "focus": "biceps, triceps",
                "exercises": [
                    ("bicep_curl", 4, "10-12", 60),
                    ("hammer_curl", 4, "10-12", 60),
                    ("tricep_pushdown", 4, "10-12", 60),
                    ("skull_crusher", 4, "8-12", 60),
                ],
            },
            {
                "name": "Leg Day",
                "name_ka": "ფეხების დღე",
                "focus": "quads, hamstrings, calves",
                "exercises": [
                    ("back_squat", 4, "6-8", 180),
                    ("romanian_deadlift", 4, "6-10", 150),
                    ("leg_press", 4, "10-12", 120),
                    ("leg_curl", 4, "10-15", 60),
                    ("walking_lunge", 3, "10-12", 90),
                    ("calf_raise", 5, "12-20", 60),
                ],
            },
        ],
    },
    {
        "name": "PPL + Upper / Lower (5-Day)",
        "name_ka": "PPL + ზედა / ქვედა (5-დღიანი)",
        "description": (
            "An advanced 5-day hybrid that combines a PPL rotation with extra upper/lower sessions for maximum "
            "frequency. Each muscle group is hit roughly twice per week with mixed strength and hypertrophy work."
        ),
        "description_ka": (
            "მოწინავე 5-დღიანი ჰიბრიდი — PPL ციკლი + ზედა/ქვედა დამატებითი დღეები. "
            "თითოეული კუნთი დაახლოებით ორჯერ კვირაში."
        ),
        "image_url": "https://images.unsplash.com/photo-1583454110551-21f2fa2afe61?w=600",
        "days_per_week": 5,
        "split_type": "ppl_upper_lower",
        "level": "advanced",
        "days": [
            {
                "name": "Push (Heavy)",
                "name_ka": "ბიძგი (მძიმე)",
                "focus": "chest, shoulders, triceps",
                "exercises": [
                    ("bench_press", 5, "4-6", 180),
                    ("overhead_press", 4, "6-8", 150),
                    ("incline_db_press", 3, "8-12", 90),
                    ("lateral_raise", 4, "12-15", 60),
                    ("tricep_pushdown", 3, "8-12", 60),
                ],
            },
            {
                "name": "Pull (Heavy)",
                "name_ka": "გაწევა (მძიმე)",
                "focus": "back, biceps",
                "exercises": [
                    ("barbell_row", 5, "4-6", 180),
                    ("pull_ups", 4, "6-10", 120),
                    ("seated_row", 3, "8-12", 90),
                    ("face_pulls", 3, "12-15", 60),
                    ("bicep_curl", 4, "8-12", 60),
                ],
            },
            {
                "name": "Legs (Heavy)",
                "name_ka": "ფეხები (მძიმე)",
                "focus": "legs",
                "exercises": [
                    ("back_squat", 5, "4-6", 180),
                    ("romanian_deadlift", 4, "6-8", 150),
                    ("leg_press", 3, "10-12", 120),
                    ("leg_curl", 3, "10-12", 60),
                    ("calf_raise", 4, "12-15", 60),
                ],
            },
            {
                "name": "Upper (Volume)",
                "name_ka": "ზედა (მოცულობა)",
                "focus": "upper body hypertrophy",
                "exercises": [
                    ("incline_db_press", 4, "10-12", 90),
                    ("lat_pulldown", 4, "10-12", 90),
                    ("cable_fly", 3, "12-15", 60),
                    ("rear_delt_fly", 3, "12-15", 60),
                    ("hammer_curl", 3, "10-12", 60),
                    ("skull_crusher", 3, "10-12", 60),
                ],
            },
            {
                "name": "Lower (Volume)",
                "name_ka": "ქვედა (მოცულობა)",
                "focus": "lower body hypertrophy",
                "exercises": [
                    ("leg_press", 4, "12-15", 90),
                    ("walking_lunge", 3, "10-12", 90),
                    ("leg_curl", 4, "12-15", 60),
                    ("calf_raise", 5, "15-20", 45),
                    ("hanging_leg_raise", 3, "10-15", 60),
                    ("cable_crunch", 3, "12-15", 60),
                ],
            },
        ],
    },
]


def build_plan_models(spec: dict) -> WorkoutPlan:
    """Build a WorkoutPlan instance (with days + exercises) from a seed spec."""
    plan = WorkoutPlan(
        name=spec["name"],
        name_ka=spec.get("name_ka"),
        description=spec["description"],
        description_ka=spec.get("description_ka"),
        image_url=spec.get("image_url"),
        days_per_week=spec["days_per_week"],
        split_type=spec["split_type"],
        level=spec.get("level", "intermediate"),
        is_default=True,
    )
    for d_idx, day_spec in enumerate(spec["days"], start=1):
        day = WorkoutDay(
            day_number=d_idx,
            name=day_spec["name"],
            name_ka=day_spec.get("name_ka"),
            focus=day_spec.get("focus"),
        )
        for o_idx, (ex_key, sets, reps, rest) in enumerate(day_spec["exercises"]):
            tpl = E[ex_key]
            lo, hi = _parse_reps(reps)
            day.exercises.append(
                Exercise(
                    order_index=o_idx,
                    name=tpl["name"],
                    name_ka=tpl.get("name_ka"),
                    description=tpl["description"],
                    description_ka=tpl.get("description_ka"),
                    image_url=tpl.get("image_url"),
                    sets=sets,
                    rep_low=lo,
                    rep_high=hi,
                    rest_seconds=rest,
                    primary_purpose=purpose_from_reps(lo, hi),
                    muscle_group=tpl["muscle_group"],
                ),
            )
        plan.days.append(day)
    return plan
