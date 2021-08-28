from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler

from mealie.core.config import app_dirs, settings

app_dirs.DATA_DIR.joinpath("scheduler.db").unlink(missing_ok=True)
scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(settings.SCHEDULER_DATABASE)})
