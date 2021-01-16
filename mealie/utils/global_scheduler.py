from services.scheduler_services import Scheduler


def start_scheduler():
    global scheduler
    scheduler = Scheduler()
    scheduler.startup_scheduler()
    return scheduler


scheduler = start_scheduler()
