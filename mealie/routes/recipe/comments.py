from http.client import HTTPException

from fastapi import Depends, status
from sqlalchemy.orm.session import Session

from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.core.dependencies import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.schema.recipe import CommentOut, CreateComment, SaveComment
from mealie.schema.user import UserInDB

router = UserAPIRouter()


@router.post("/{slug}/comments")
async def create_comment(
    slug: str,
    new_comment: CreateComment,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Create comment in the Database """

    new_comment = SaveComment(user=current_user.id, text=new_comment.text, recipe_slug=slug)
    return db.comments.create(session, new_comment)


@router.put("/{slug}/comments/{id}")
async def update_comment(
    id: int,
    new_comment: CreateComment,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Update comment in the Database """
    old_comment: CommentOut = db.comments.get(session, id)

    if current_user.id != old_comment.user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return db.comments.update(session, id, new_comment)


@router.delete("/{slug}/comments/{id}")
async def delete_comment(
    id: int, session: Session = Depends(generate_session), current_user: UserInDB = Depends(get_current_user)
):
    """ Delete comment from the Database """
    comment: CommentOut = db.comments.get(session, id)
    if current_user.id == comment.user.id or current_user.admin:
        db.comments.delete(session, id)
        return

    raise HTTPException(status.HTTP_403_FORBIDDEN)
