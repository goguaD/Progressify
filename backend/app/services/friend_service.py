from app.repositories.friend_repo import FriendRepository
from app.schemas import FriendshipState


def friendship_state(
    repo: FriendRepository, viewer_id: int, target_id: int
) -> tuple[FriendshipState, int | None]:
    if viewer_id == target_id:
        return "self", None
    row = repo.find_between(viewer_id, target_id)
    if not row:
        return "none", None
    if row.status == "accepted":
        return "friends", row.id
    if row.status == "pending":
        if row.requester_id == viewer_id:
            return "pending_outgoing", row.id
        return "pending_incoming", row.id
    return "none", None
