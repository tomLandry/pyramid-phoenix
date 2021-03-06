from pyramid.events import subscriber

from phoenix.events import JobFinished, JobStarted

import logging
logger = logging.getLogger(__name__)


@subscriber(JobStarted)
def notify_job_started(event):
    event.request.session.flash("Job added to task queue. Please wait ...", queue='info')


@subscriber(JobFinished)
def notify_job_finished(event):
    if event.succeeded():
        logger.info("job %s succeded.", event.job.get('title'))
        # event.request.session.flash("Job <b>{0}</b> succeded.".format(event.job.get('title')), queue='success')
    else:
        logger.warn("job %s failed.", event.job.get('title'))
        # logger.warn("status = %s", event.job.get('status'))
        # event.request.session.flash("Job <b>{0}</b> failed.".format(event.job.get('title')), queue='danger')


