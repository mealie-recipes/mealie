from http.client import HTTPException

from fastapi import Depends, status
from mealie.db.database import db
from mealie.db.db_setup import generate_session
from mealie.routes.deps import get_current_user
from mealie.routes.routers import UserAPIRouter
from mealie.schema.comments import CommentIn, CommentOut, CommentSaveToDB
from mealie.schema.user import UserInDB
from sqlalchemy.orm.session import Session

router = UserAPIRouter(prefix="/api", tags=["Recipe Comments"])


@router.post("/recipes/{slug}/comments")
async def create_comment(
    slug: str,
    new_comment: CommentIn,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Create comment in the Database """

    new_comment = CommentSaveToDB(user=current_user.id, text=new_comment.text, recipe_slug=slug)
    return db.comments.create(session, new_comment)


@router.put("/recipes/{slug}/comments/{id}")
async def update_comment(
    id: int,
    new_comment: CommentIn,
    session: Session = Depends(generate_session),
    current_user: UserInDB = Depends(get_current_user),
):
    """ Update comment in the Database """
    old_comment: CommentOut = db.comments.get(session, id)

    if current_user.id != old_comment.user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    return db.comments.update(session, id, new_comment)


@router.delete("/recipes/{slug}/comments/{id}")
async def delete_comment(
    id: int, session: Session = Depends(generate_session), current_user: UserInDB = Depends(get_current_user)
):
    """ Delete comment from the Database """
    comment: CommentOut = db.comments.get(session, id)
    print(current_user.id, comment.user.id, current_user.admin)
    if current_user.id == comment.user.id or current_user.admin:
        db.comments.delete(session, id)
        return

    raise HTTPException(status.HTTP_403_FORBIDDEN)
