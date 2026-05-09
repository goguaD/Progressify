from sqlalchemy.orm import Session

from app.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username.lower()).first()

    def search_by_username(
        self,
        needle: str,
        exclude_id: int,
        *,
        hide_admins: bool = False,
        limit: int = 15,
    ) -> list[User]:
        q = (
            self.db.query(User)
            .filter(User.username.ilike(f"%{needle}%"))
            .filter(User.id != exclude_id)
        )
        if hide_admins:
            q = q.filter(User.role != "admin")
        return q.order_by(User.username.asc()).limit(limit).all()

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def list_all(self) -> list[User]:
        return self.db.query(User).order_by(User.id.asc()).all()

    def save(self) -> None:
        self.db.commit()

    def refresh(self, user: User) -> None:
        self.db.refresh(user)
