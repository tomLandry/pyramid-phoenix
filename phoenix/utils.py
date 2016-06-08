import os
import tempfile
from datetime import datetime
from datetime import timedelta
from dateutil import parser as datetime_parser

from owslib.util import build_get_url

import deform

from pyramid.url import resource_url
from pyramid.security import authenticated_userid

from phoenix.security import auth_protocols

import logging
logger = logging.getLogger(__name__)

SIGNIN_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign in"><span class="fa fa-sign-in"></span></a>'
SIGNOUT_HTML = '<a class="navbar-link btn-lg" href="%s" data-toggle="tooltip" title="Sign out %s"><span class="fa fa-sign-out"></span></a>'

# buttons
# see kotti: https://github.com/Kotti/Kotti
# TODO: maybe use deform.Button instead of ActionButton

class ActionButton(object):
    def __init__(self, name, title=None, no_children=False, href=None, new_window=False,
                 disabled=False, css_class=u"btn btn-default",
                 icon=None):
        self.name = name
        if title is None:
            title = name.replace('-', ' ').replace('_', ' ').title()
        self.title = title
        self.no_children = no_children
        self.css_class = css_class
        if disabled:
            self.css_class = self.css_class + " disabled"
        self.icon = icon
        if href is None:
            href = '/' + self.name
        self.href = href
        self.new_window = new_window

    def url(self, context, request):
        return self.href

    def permitted(self, context, request):
        return True

    def __eq__(self, other):
        return isinstance(other, ActionButton) and repr(self) == repr(other)

    def __repr__(self):
        return u'ActionButton({0}, {1})'.format(self.name, self.title)


# upload helpers

def save_upload(request, filename, fs=None):
    folder=authenticated_userid(request)
    path = os.path.join(folder, os.path.basename(filename))
    if request.storage.exists(path):
        request.storage.delete(path)
    stored_filename = None
    if fs is None:
        stored_filename = request.storage.save_filename(filename, folder=folder)
    else:
        stored_filename = request.storage.save_file(fs.file, filename=os.path.basename(path), folder=folder)
    logger.debug('saved file to upload storage %s', stored_filename)

    
def save_chunk(fs, path):
    """
    Save an uploaded chunk.
    
    Chunks are stored in chunks/
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        destination.write(fs.read())

        
def combine_chunks(total_parts, source_folder, dest):
    """
    Combine a chunked file into a whole file again. Goes through each part
    , in order, and appends that part's bytes to another destination file.
    
    Chunks are stored in chunks/
    """

    logger.debug("Combining chunks: %s", source_folder)
    
    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in xrange(int(total_parts)):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())
        logger.debug("Combined: %s", dest)

# misc

def format_labels(labels):
    label_list = [label.strip().lower() for label in labels.split(',') if len(label.strip()) > 0]
    label_list.sort()
    new_labels = ', '.join(label_list)
    return new_labels


def button(request):
    """If the user is logged in, returns the logout button, otherwise returns the login button"""
    import markupsafe
    
    if not authenticated_userid(request):
        protocols = auth_protocols(request)
        if len(protocols) > 0:
            protocol = protocols[-1]
        else:
            protocol = 'oauth2'
        return markupsafe.Markup(SIGNIN_HTML) % (request.route_path('account_login', protocol=protocol))
    else:
        return markupsafe.Markup(SIGNOUT_HTML) % (request.route_path('account_logout'), authenticated_userid(request))


def localize_datetime(dt, tz_name='UTC'):
    """Provide a timzeone-aware object for a given datetime and timezone name
    """
    import pytz
    assert dt.tzinfo == None
    utc = pytz.timezone('UTC')
    aware = utc.localize(dt)
    timezone = pytz.timezone(tz_name)
    tz_aware_dt = aware.astimezone(timezone)
    return tz_aware_dt

def get_user(request):
    userid = authenticated_userid(request)
    return request.db.users.find_one(dict(identifier=userid))

def user_cert_valid(request, valid_hours=6):
    cert_expires = get_user(request).get('cert_expires')
    if cert_expires != None:
        timestamp = datetime_parser.parse(cert_expires)
        now = localize_datetime(datetime.utcnow())
        valid_hours = timedelta(hours=valid_hours)
        # cert must be valid for some hours
        if timestamp > now + valid_hours:
            return True
    return False

def is_url(url):
    """Check wheather given text is url or not
    """
    from urlparse import urlparse
    return bool(urlparse(url ).scheme)

def build_url(url, query):
    import urllib
    if not url.endswith('?'):
        url = url + '?'
    return url + urllib.urlencode(query)

def wps_caps_url(url):
    # TODO: move code to owslib?
    params = {'service': 'WPS', 'request': 'GetCapabilities', 'version': '1.0.0'}
    return build_get_url(url, params, overwrite=True)

def wps_describe_url(url, identifier):
    # TODO: move code to owslib?
    params = {'service': 'WPS', 'request': 'DescribeProcess', 'version': '1.0.0', 'identifier': identifier}
    return build_get_url(url, params, overwrite=True)

def time_ago_in_words(from_time):
    from webhelpers2.date import time_ago_in_words as _time_ago_in_words
    try:
        delta = datetime.now() - from_time
        granularity='minute'
        if delta.days > 365:
            granularity = 'year'
        elif delta.days > 30:
            granularity = 'month'
        elif delta.days > 0:
            granularity = 'day'
        elif delta.total_seconds() > 3600:
            granularity = 'hour'
        time_ago = _time_ago_in_words(from_time, granularity=granularity)
        time_ago = time_ago + " ago"
    except:
        time_ago = '???'
    finally:
        return time_ago

def root_path(path):
    try:
        return path.split(os.sep, 2)[1]
    except:
        return None
    
