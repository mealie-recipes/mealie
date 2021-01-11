from services.scheduler_services import Scheduler

scheduler = None

def start_scheduler():
    global scheduler
    scheduler = Scheduler()
    scheduler.startup_scheduler()
