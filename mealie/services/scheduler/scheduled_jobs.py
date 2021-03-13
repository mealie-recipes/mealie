from apscheduler.schedulers.background import BackgroundScheduler
from db.db_setup import create_session
from services.backups.exports import auto_backup_job
from services.scheduler.global_scheduler import scheduler
from services.scheduler.scheduler_utils import Cron, cron_parser
from fastapi.logger import logger
from schema.settings import SiteSettings
from db.database import db
from utils.post_webhooks import post_webhooks

# TODO Fix Scheduler
@scheduler.scheduled_job(trigger="interval", minutes=15)
def update_webhook_schedule():
    """
    A scheduled background job that runs every 15 minutes to
    poll the database for changes and reschedule the webhook time
    """
    session = create_session()
    settings = db.settings.get(session, "main")
    settings = SiteSettings(**settings)
    time = cron_parser(settings.webhooks.webhookTime)
    job = JOB_STORE.get("webhooks")

    scheduler.reschedule_job(
        job.scheduled_task.id,
        trigger="cron",
        hour=time.hours,
        minute=time.minutes,
    )

    session.close()
    logger.info(scheduler.print_jobs())


class ScheduledFunction:
    def __init__(
        self, scheduler: BackgroundScheduler, function, cron: Cron, name: str
    ) -> None:
        self.scheduled_task = scheduler.add_job(
            function,
            trigger="cron",
            name=name,
            hour=cron.hours,
            minute=cron.minutes,
            max_instances=1,
            replace_existing=True,
        )

        logger.info("New Function Scheduled")
        logger.info(scheduler.print_jobs())


logger.info("----INIT SCHEDULE OBJECT-----")

JOB_STORE = {
    "backup_job": ScheduledFunction(
        scheduler, auto_backup_job, Cron(hours=00, minutes=00), "backups"
    ),
    "webhooks": ScheduledFunction(
        scheduler, post_webhooks, Cron(hours=00, minutes=00), "webhooks"
    ),
}

scheduler.start()
