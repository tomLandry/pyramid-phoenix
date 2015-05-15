from pyramid_celery import celery_app as app
from phoenix.models import mongodb

@app.task
def execute(email, url, identifier, inputs, outputs, workflow=False, keywords=None):
    from owslib.wps import WebProcessingService
    wps = WebProcessingService(url=url, skip_caps=True)
    execution = wps.execute(identifier, inputs=inputs, output=outputs)
    db = mongodb(app.conf['PYRAMID_REGISTRY'])
    import uuid
    from datetime import datetime
    job = dict(
        identifier = uuid.uuid4().get_hex(),
        workflow = workflow,
        title = execution.process.title,
        abstract = execution.process.abstract,
        keywords = keywords,
        email = email,
        wps_url = execution.serviceInstance,
        status_location = execution.statusLocation,
        created = datetime.now(),
        is_complete = False)
    db.jobs.save(job)
    while not execution.isComplete():
        execution.checkStatus(sleepSecs=2)
        job['status'] = execution.getStatus()
        job['status_message'] = execution.statusMessage
        job['is_complete'] = execution.isComplete()
        job['is_succeded'] = execution.isSucceded()
        job['errors'] = [ '%s %s\n: %s' % (error.code, error.locator, error.text.replace('\\','')) for error in execution.errors]
        duration = datetime.now() - job.get('created', datetime.now())
        job['duration'] = str(duration).split('.')[0]
        if execution.isComplete():
            job['finished'] = datetime.now()
        if execution.isSucceded():
            job['progress'] = 100
        else:
            job['progress'] = execution.percentCompleted
        # update db
        db.jobs.update({'identifier': job['identifier']}, job)
    return execution.getStatus()