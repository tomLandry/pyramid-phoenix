import uuid
import datetime

import logging
logger = logging.getLogger(__name__)

def add_user(
    request,
    email,
    openid='',
    name='unknown',
    organisation='unknown',
    notes='',
    activated=False):
    user=dict(
        identifier = uuid.uuid4().get_urn(),
        email = email,
        openid = openid,
        name = name,
        organisation = organisation,
        notes = notes,
        activated = activated,
        creation_time = datetime.datetime.now(),
        last_login = datetime.datetime.now())
    request.db.users.save(user)
    return request.db.users.find_one({'email':email})

def add_job(request, wps_url, status_location, notes=None, tags=None):
    from pyramid.security import authenticated_userid

    logger.debug("add job: status_location=%s", status_location)

    job = dict(
        # TODO: need job name ...
        #identifier = uuid.uuid4().get_urn(), # TODO: urn does not work as id in javascript
        identifier = uuid.uuid4().get_hex(),
        #TODO: dont use auth... userid=email ...
        email = authenticated_userid(request),
        wps_url = wps_url,
        status_location = status_location,
        notes = notes,
        tags = tags)
    request.db.jobs.save(job)

def user_stats(request):
    d = datetime.datetime.now() - datetime.timedelta(hours=3)
    num_logins_3h = request.db.users.find({"last_login": {"$gt": d}}).count()

    d = datetime.datetime.now() - datetime.timedelta(days=7)
    num_logins_7d = request.db.users.find({"last_login": {"$gt": d}}).count()

    return dict(num_users=request.db.users.count(),
                num_logins_3h=num_logins_3h,
                num_logins_7d=num_logins_7d)

def get_wps_list(request):
    csw = request.csw
    csw.getrecords(
        qtype="service",
        esn="full",
        propertyname="dc:format",
        keywords=['WPS'])
    items = []
    for rec in csw.records:
        items.append(dict(
            identifier=csw.records[rec].identifier,
            title=csw.records[rec].title,
            subjects=csw.records[rec].subjects,
            abstract=csw.records[rec].abstract,
            references=csw.records[rec].references,
            format=csw.records[rec].format,
            source=csw.records[rec].source,
            rights=csw.records[rec].rights))
    return items





    
