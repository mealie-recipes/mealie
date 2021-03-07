import shutil
from datetime import timedelta

from core.config import USER_DIR
from core.security import get_password_hash, verify_password
from db.database import db
from db.db_setup import generate_session
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import FileResponse
from routes.deps import manager
from schema.snackbar import SnackResponse
from schema.user import GroupBase, GroupInDB
from sqlalchemy.orm.session import Session

router = APIRouter(prefix="/api/groups", tags=["Groups"])


@router.get("", response_model=list[GroupInDB])
async def get_all_groups(
    current_user=Depends(manager),
    session: Session = Depends(generate_session),
):
    """ Returns a list of all groups in the database """
    return db.groups.get_all(session)
