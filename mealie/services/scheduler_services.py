import collections
import json

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from utils.logger import logger

from services.backups.export import auto_backup_job
from services.meal_services import MealPlan
from services.recipe_services import Recipe
from services.settings_services import SiteSettings

Cron = collections.namedtuple("Cron", "hours minutes")


def cron_parser(time_str: str) -> Cron:
    time = time_str.split(":")
    cron = Cron(hours=int(time[0]), minutes=int(time[1]))

    return cron


def post_webhooks():
    all_settings = SiteSettings.get_site_settings()

    if all_settings.webhooks.enabled:
        todays_meal = Recipe.get_by_slug(MealPlan.today()).dict()
        urls = all_settings.webhooks.webhookURLs

        for url in urls:
            requests.post(url, json.dumps(todays_meal, default=str))


class Scheduler:
    def startup_scheduler(self):
        self.scheduler = BackgroundScheduler()
        logger.info("----INIT SCHEDULE OBJECT-----")
        self.scheduler.start()

        self.scheduler.add_job(
            auto_backup_job, trigger="cron", hour="3", max_instances=1
        )
        settings = SiteSettings.get_site_settings()
        time = cron_parser(settings.webhooks.webhookTime)

        self.webhook = self.scheduler.add_job(
            post_webhooks,
            trigger="cron",
            name="webhooks",
            hour=time.hours,
            minute=time.minutes,
            max_instances=1,
        )

        logger.info(self.scheduler.print_jobs())

    def reschedule_webhooks(self):
        """
        Reads the site settings database entry to reschedule the webhooks task
        Called after each post to the webhooks endpoint.
        """
        settings = SiteSettings.get_site_settings()
        time = cron_parser(settings.webhooks.webhookTime)

        self.scheduler.reschedule_job(
            self.webhook.id,
            trigger="cron",
            hour=time.hours,
            minute=time.minutes,
        )

        logger.info(self.scheduler.print_jobs())
