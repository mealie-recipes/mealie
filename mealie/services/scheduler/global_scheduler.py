from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from mealie.core.config import settings

scheduler = BackgroundScheduler(jobstores={"default": SQLAlchemyJobStore(settings.SCHEDULER_DATABASE)})
