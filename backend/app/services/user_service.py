from datetime import UTC, datetime, timedelta

from app.config import ONLINE_WINDOW
from app.models import User


def is_online(user: User) -> bool:
    if not user.is_online or not user.last_seen:
        return False
    last = user.last_seen
    if last.tzinfo is None:
        last = last.replace(tzinfo=UTC)
    return (datetime.now(UTC) - last) <= ONLINE_WINDOW


def public_user_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "goal": user.goal,
        "weight": user.weight,
        "height": user.height,
        "age": user.age,
        "gender": user.gender,
        "avatar_url": user.avatar_url,
        "role": user.role,
        "last_seen": user.last_seen,
        "is_online": is_online(user),
    }


def placeholder_activity(user: User) -> dict[str, str]:
    """Until workouts/mealplans tables exist, fabricate a friendly blurb
    so the friends feed has something to show."""
    workouts_by_goal: dict[str, str] = {
        "muscle_gain": "Push Day \u00b7 Chest & Triceps",
        "weight_loss": "HIIT Cardio \u00b7 30 min",
        "maintain": "Full Body \u00b7 Maintenance",
        "endurance": "Long Run \u00b7 8 km",
        "flexibility": "Yoga Flow \u00b7 45 min",
    }
    meals_by_goal: dict[str, str] = {
        "muscle_gain": "High-Protein Bulk",
        "weight_loss": "Calorie Deficit Plan",
        "maintain": "Balanced Macros",
        "endurance": "Carb-Forward Plan",
        "flexibility": "Mediterranean Plan",
    }
    workout = workouts_by_goal.get(user.goal or "", "No workout yet")
    meal = meals_by_goal.get(user.goal or "", "No meal plan yet")

    if user.last_seen:
        last = user.last_seen
        if last.tzinfo is None:
            last = last.replace(tzinfo=UTC)
        delta = datetime.now(UTC) - last
        if user.is_online and delta < timedelta(minutes=5):
            activity = "Active right now"
        elif delta < timedelta(hours=1):
            mins = int(delta.total_seconds() // 60)
            activity = f"Last seen {mins} min ago"
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() // 3600)
            activity = f"Last seen {hours}h ago"
        else:
            days = delta.days
            activity = f"Last seen {days}d ago"
    else:
        activity = "Hasn't logged in yet"

    return {
        "current_workout": workout,
        "current_meal_plan": meal,
        "last_activity": activity,
    }
