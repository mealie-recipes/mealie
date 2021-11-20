from http.client import HTTPException

from fastapi import Depends, status
from sqlalchemy.orm.session import Session

from mealie.core.dependencies import get_current_user
from mealie.db.database import get_database
from mealie.db.db_setup import generate_session
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CommentOut, CreateComment, SaveComment
from mealie.schema.user import PrivateUser

router = UserAPIRouter()


@router.post("/{slug}/comments")
async def create_comment(
    slug: str,
    new_comment: CreateComment,
    session: Session = Depends(generate_session),
    current_user: PrivateUser = Depends(get_current_user),
):
    """Create comment in the Database"""
    db = get_database(session)

    new_comment = SaveComment(user=current_user.id, text=new_comment.text, recipe_slug=slug)
    return db.comments.create(new_comment)


@router.put("/{slug}/comments/{id}")
async def update_comment(
    id: int,
    new_comment: CreateComment,
    session: Session = Depends(generate_session),
    current_user: PrivateUser = Depends(get_current_user),
):
    """Update comment in the Database"""
    db = get_database(session)
    old_comment: CommentOut = db.comments.get(id)

    if current_user.id != old_comment.user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return db.comments.update(id, new_comment)


@router.delete("/{slug}/comments/{id}")
async def delete_comment(
    id: int, session: Session = Depends(generate_session), current_user: PrivateUser = Depends(get_current_user)
):
    """Delete comment from the Database"""
    db = get_database(session)
    comment: CommentOut = db.comments.get(id)
    if current_user.id == comment.user.id or current_user.admin:
        db.comments.delete(id)
        return

    raise HTTPException(status.HTTP_403_FORBIDDEN)
