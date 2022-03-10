from apscheduler.schedulers.background import BackgroundScheduler
from tesla_ce_supervisor.jobs.tasks import update_deploy_status


def start_jobs():
    scheduler = BackgroundScheduler()

    # Add our task to scheduler.
    scheduler.add_job(update_deploy_status, 'interval', seconds=10)

    # And finally start.
    scheduler.start()
