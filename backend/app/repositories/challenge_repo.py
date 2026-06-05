from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models import Challenge


class ChallengeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, challenge_id: int) -> Challenge | None:
        return self.db.query(Challenge).filter(Challenge.id == challenge_id).first()

    def list_for_user(self, user_id: int, *, status: str | None = None) -> list[Challenge]:
        q = self.db.query(Challenge).filter(
            or_(
                Challenge.challenger_id == user_id,
                Challenge.opponent_id == user_id,
            )
        )
        if status:
            q = q.filter(Challenge.status == status)
        return q.order_by(Challenge.created_at.desc()).all()

    def completed_between(self, user_a: int, user_b: int) -> list[Challenge]:
        return (
            self.db.query(Challenge)
            .filter(
                Challenge.status == "completed",
                or_(
                    and_(
                        Challenge.challenger_id == user_a,
                        Challenge.opponent_id == user_b,
                    ),
                    and_(
                        Challenge.challenger_id == user_b,
                        Challenge.opponent_id == user_a,
                    ),
                ),
            )
            .all()
        )

    def create(self, challenge: Challenge) -> Challenge:
        self.db.add(challenge)
        self.db.commit()
        self.db.refresh(challenge)
        return challenge

    def save(self) -> None:
        self.db.commit()

    def refresh(self, challenge: Challenge) -> None:
        self.db.refresh(challenge)
