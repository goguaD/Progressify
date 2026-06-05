from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.models import Friendship


class FriendRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def accepted_friend_ids(self, user_id: int) -> set[int]:
        rows = (
            self.db.query(Friendship)
            .filter(
                Friendship.status == "accepted",
                or_(
                    Friendship.requester_id == user_id,
                    Friendship.addressee_id == user_id,
                ),
            )
            .all()
        )
        ids: set[int] = set()
        for r in rows:
            ids.add(r.requester_id if r.requester_id != user_id else r.addressee_id)
        return ids

    def find_between(self, user_a: int, user_b: int) -> Friendship | None:
        return (
            self.db.query(Friendship)
            .filter(
                or_(
                    and_(
                        Friendship.requester_id == user_a,
                        Friendship.addressee_id == user_b,
                    ),
                    and_(
                        Friendship.requester_id == user_b,
                        Friendship.addressee_id == user_a,
                    ),
                )
            )
            .first()
        )

    def find_accepted_between(self, user_a: int, user_b: int) -> Friendship | None:
        return (
            self.db.query(Friendship)
            .filter(
                Friendship.status == "accepted",
                or_(
                    and_(
                        Friendship.requester_id == user_a,
                        Friendship.addressee_id == user_b,
                    ),
                    and_(
                        Friendship.requester_id == user_b,
                        Friendship.addressee_id == user_a,
                    ),
                ),
            )
            .first()
        )

    def get_by_id(self, request_id: int) -> Friendship | None:
        return self.db.query(Friendship).filter(Friendship.id == request_id).first()

    def pending_for_user(self, user_id: int) -> list[Friendship]:
        return (
            self.db.query(Friendship)
            .filter(
                Friendship.status == "pending",
                Friendship.addressee_id == user_id,
            )
            .order_by(Friendship.created_at.desc())
            .all()
        )

    def create(self, friendship: Friendship) -> Friendship:
        self.db.add(friendship)
        self.db.commit()
        return friendship

    def delete(self, friendship: Friendship) -> None:
        self.db.delete(friendship)
        self.db.commit()

    def save(self) -> None:
        self.db.commit()
