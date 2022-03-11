import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from tesla_ce_supervisor.jobs.tasks import update_deploy_status

logger = logging.getLogger('background_tasks')


def start_jobs():
    logger.info('Enabling Scheduler')
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Add our task to scheduler.
    try:
        scheduler.add_job(update_deploy_status, 'interval', seconds=10)
    except Exception:
        pass

    # And finally start.
    scheduler.start()
