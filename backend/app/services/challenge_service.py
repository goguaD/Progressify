from datetime import UTC, datetime

from app.models import Challenge
from app.repositories.challenge_repo import ChallengeRepository
from app.services.user_service import is_online


def safe_deadline(ch: Challenge) -> datetime | None:
    if ch.deadline is None:
        return None
    dl = ch.deadline
    return dl.replace(tzinfo=UTC) if dl.tzinfo is None else dl


def parse_result(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(raw)
    except (ValueError, TypeError):
        return None


def challenge_user_brief(user: object) -> dict:
    return {
        "id": user.id,  # type: ignore[attr-defined]
        "username": user.username,  # type: ignore[attr-defined]
        "firstname": user.firstname,  # type: ignore[attr-defined]
        "lastname": user.lastname,  # type: ignore[attr-defined]
        "avatar_url": user.avatar_url,  # type: ignore[attr-defined]
        "is_online": is_online(user),  # type: ignore[arg-type]
    }


def challenge_out(ch: Challenge, viewer_id: int) -> dict:
    is_challenger = ch.challenger_id == viewer_id
    both_submitted = ch.challenger_submitted_at is not None and ch.opponent_submitted_at is not None
    dl = safe_deadline(ch)
    is_past = dl is not None and datetime.now(UTC) >= dl
    reveal = both_submitted or is_past or ch.status == "completed"

    my_result_raw = ch.challenger_result if is_challenger else ch.opponent_result
    their_result_raw = ch.opponent_result if is_challenger else ch.challenger_result
    my_submitted_at = ch.challenger_submitted_at if is_challenger else ch.opponent_submitted_at
    their_submitted_at = ch.opponent_submitted_at if is_challenger else ch.challenger_submitted_at

    hours_left = (dl - datetime.now(UTC)).total_seconds() / 3600 if dl else 999

    return {
        "id": ch.id,
        "challenger": challenge_user_brief(ch.challenger),
        "opponent": challenge_user_brief(ch.opponent),
        "challenge_type": ch.challenge_type,
        "message": ch.message,
        "deadline": ch.deadline,
        "status": ch.status,
        "created_at": ch.created_at,
        "muscle_group": ch.muscle_group,
        "endurance_mode": ch.endurance_mode,
        "endurance_speed": ch.endurance_speed,
        "endurance_gradient": ch.endurance_gradient,
        "target_weight_kg": ch.target_weight_kg,
        "my_result": parse_result(my_result_raw) if reveal else None,
        "their_result": parse_result(their_result_raw) if reveal else None,
        "my_submitted": my_submitted_at is not None,
        "their_submitted": their_submitted_at is not None,
        "winner": challenge_user_brief(ch.winner) if ch.winner else None,
        "deadline_soon": 0 < hours_left <= 24 and ch.status == "accepted",
    }


def resolve_challenge(ch: Challenge, repo: ChallengeRepository) -> None:
    """Determine the winner.

    - strength: higher kg wins
    - endurance: longer time (seconds) wins
    - target_weight: first to submit wins (goal reached)
    """
    dl = safe_deadline(ch)
    is_past = dl is not None and datetime.now(UTC) >= dl
    both = ch.challenger_submitted_at is not None and ch.opponent_submitted_at is not None

    if ch.challenge_type == "target_weight":
        if ch.challenger_submitted_at and not ch.opponent_submitted_at:
            ch.winner_id = ch.challenger_id
            ch.status = "completed"
            repo.save()
            return
        if ch.opponent_submitted_at and not ch.challenger_submitted_at:
            ch.winner_id = ch.opponent_id
            ch.status = "completed"
            repo.save()
            return
        if both:
            if ch.challenger_submitted_at <= ch.opponent_submitted_at:  # type: ignore[operator]
                ch.winner_id = ch.challenger_id
            else:
                ch.winner_id = ch.opponent_id
            ch.status = "completed"
            repo.save()
            return
        return

    if not both and not is_past:
        return

    c_val = parse_result(ch.challenger_result)
    o_val = parse_result(ch.opponent_result)

    if c_val is not None and o_val is None:
        ch.winner_id = ch.challenger_id
    elif o_val is not None and c_val is None:
        ch.winner_id = ch.opponent_id
    elif c_val is not None and o_val is not None:
        if c_val > o_val:
            ch.winner_id = ch.challenger_id
        elif o_val > c_val:
            ch.winner_id = ch.opponent_id
        else:
            ch.winner_id = None
    else:
        ch.winner_id = None

    ch.status = "completed"
    repo.save()


def compute_h2h(repo: ChallengeRepository, current_id: int, opponent_id: int) -> dict[str, int]:
    completed = repo.completed_between(current_id, opponent_id)
    wins = sum(1 for c in completed if c.winner_id == current_id)
    losses = sum(1 for c in completed if c.winner_id == opponent_id)
    draws = len(completed) - wins - losses
    return {"wins": wins, "losses": losses, "draws": draws}
