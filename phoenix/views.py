# views.py
# Copyright (C) 2013 the ClimDaPs/Phoenix authors and contributors
# <see AUTHORS file>
#
# This module is part of ClimDaPs/Phoenix and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import os
import datetime

from pyramid.view import view_config, forbidden_view_config
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.security import remember, forget, authenticated_userid
from pyramid.events import subscriber, BeforeRender
from pyramid_deform import FormView
from deform import Form
from deform.form import Button
from authomatic import Authomatic
from authomatic.adapters import WebObAdapter
import config_public as config

from owslib.csw import CatalogueServiceWeb
from owslib.wps import WebProcessingService, WPSExecution, ComplexData

from .security import is_valid_user

from .wps import WPSSchema  

from .helpers import wps_url
from .helpers import csw_url
from .helpers import supervisor_url
from .helpers import thredds_url
from .helpers import update_wps_url
from .helpers import execute_wps

import logging

log = logging.getLogger(__name__)

authomatic = Authomatic(config=config.config,
                        secret=config.SECRET,
                        report_errors=True,
                        logging_level=logging.DEBUG)

@subscriber(BeforeRender)
def add_global(event):
    event['message_type'] = 'alert-info'
    event['message'] = ''


# Exception view
# --------------

# @view_config(context=Exception)
# def error_view(exc, request):
#     msg = exc.args[0] if exc.args else ''
#     response = Response(str(msg))
#     response.status_int = 500
#     response.content_type = 'text/xml'
#     return response


# login
# -------

@view_config(
    route_name='login', 
    layout='default', 
    renderer='templates/login.pt',
    permission='view')
def login(request):
    return dict()

# logout
# --------

@view_config(
    route_name='logout',
    permission='edit')
def logout(request):
    log.debug("logout")
    headers = forget(request)
    return HTTPFound(location = request.route_url('home'),
                     headers = headers)

# forbidden view
# --------------

@forbidden_view_config(
    renderer='templates/forbidden.pt',
    )
def forbidden(request):
    request.response.status = 403
    return dict(message=None)

# register view
# -------------
@view_config(
    route_name='register',
    permission='view')
def register(request):
    return dict()


# local login for admin and demo user
# -----------------------------------
@view_config(
    route_name='login_local',
    #check_csrf=True, 
    permission='view')
def login_local(request):
    password = request.params.get('password')
    if (password == 'Hamburg'):
        email = "demo@climdaps.org"

        if is_valid_user(request, email):
            request.response.text = render('phoenix:templates/openid_success.pt',
                                           {'result': email},
                                           request=request)
            # Add the headers required to remember the user to the response
            request.response.headers.extend(remember(request, email))
        else:
            request.response.text = render('phoenix:templates/register.pt',
                                           {'email': email}, request=request)
    else:
        request.response.text = render('phoenix:templates/forbidden.pt',
                                       {'message': 'Wrong Password'},
                                       request=request)

    return request.response

# persona login
# -------------

@view_config(
    route_name='login_persona', 
    check_csrf=True, 
    renderer='json',
    permission='view')
def login_persona(request):
    # TODO: update login to my needs
    # https://pyramid_persona.readthedocs.org/en/latest/customization.html#do-extra-work-or-verification-at-login

    log.debug('login with persona')

    # Verify the assertion and get the email of the user
    from pyramid_persona.views import verify_login 
    email = verify_login(request)
    # check whitelist
    if not is_valid_user(request, email):
        #    request.session.flash('Sorry, you are not on the list')
        return {'redirect': '/', 'success': False}
    # Add the headers required to remember the user to the response
    request.response.headers.extend(remember(request, email))
    # Return a json message containing the address or path to redirect to.
    #return {'redirect': request.POST['came_from'], 'success': True}
    return {'redirect': '/', 'success': True}

# authomatic openid login
# -----------------------

@view_config(
    route_name='login_openid',
    permission='view')
def login_openid(request):
    # Get the internal provider name URL variable.
    provider_name = request.matchdict.get('provider_name', 'openid')

    log.debug('provider_name: %s', provider_name)
    
    # Start the login procedure.
    response = Response()
    #response = request.response
    result = authomatic.login(WebObAdapter(request, response), provider_name)

    log.debug('authomatic login result: %s', result)
    
    if result:
        if result.error:
            # Login procedure finished with an error.
            #request.session.flash('Sorry, login failed: %s' % (result.error.message))
            log.error('openid login failed: %s', result.error.message)
            #response.write(u'<h2>Login failed: {}</h2>'.format(result.error.message))
            response.text = render('phoenix:templates/forbidden.pt',
                                   {'message': result.error.message}, request=request)
        elif result.user:
            # Hooray, we have the user!
            log.debug("user=%s, id=%s, email=%s",
                      result.user.name, result.user.id, result.user.email)

            if is_valid_user(request, result.user.id):
                response.text = render('phoenix:templates/openid_success.pt',
                                       {'result': result},
                                       request=request)
                # Add the headers required to remember the user to the response
                response.headers.extend(remember(request, result.user.email))
            else:
                response.text = render('phoenix:templates/register.pt',
                                       {'email': result.user.email}, request=request)
    log.debug('response: %s', response)
        
    return response

# home view
# ---------

@view_config(
    route_name='home',
    renderer='templates/home.pt',
    layout='default',
    permission='view'
    )
def home(request):
    log.debug('rendering home view')

    lm = request.layout_manager
    lm.layout.add_heading('heading_processes')
    lm.layout.add_heading('heading_jobs')
    return dict()


# processes
# ---------

@view_config(
    route_name='processes',
    renderer='templates/form.pt',
    layout='default',
    permission='edit'
    )
class ProcessView(FormView):
    from .schema import ProcessSchema

    schema = ProcessSchema(title="Select process you wish to run")
    buttons = ('submit',)

    def submit_success(self, appstruct):
        params = self.schema.serialize(appstruct)
        identifier = params.get('process')
        
        session = self.request.session
        session['phoenix.process.identifier'] = identifier
        session.changed()
        
        return HTTPFound(location=self.request.route_url('execute'))
   
# jobs
# -------

@view_config(
    route_name='jobs',
    renderer='templates/jobs.pt',
    layout='default',
    permission='edit'
    )
def jobs(request):
    from .models import jobs_information

    jobs = jobs_information(request)

    if "remove_all" in request.POST:
        from .models import drop_user_jobs
        drop_user_jobs(request)
        
        return HTTPFound(location=request.route_url('jobs'))

    elif "remove_selected" in request.POST:
        if("selected" in request.POST):
            from .models import drop_jobs_by_uuid
            drop_jobs_by_uuid(request,request.POST.getall("selected"))
        return HTTPFound(location=request.route_url('jobs'))

    return {"jobs":jobs}

@view_config(
    route_name="jobsupdate",
    renderer ="templates/jobsupdate.pt",
    layout='default',
    permission='edit'
    )
def jobsupdate(request):
    from .models import jobs_information
    data = request.matchdict
    #Sort the table with the given key, matching to the template name
    key = data["sortkey"]
    #If inverted is found as type then the ordering is inverted.
    inverted = (data["type"]=="inverted")
    jobs = jobs_information(request,key,inverted)
    return {"jobs":jobs}

# output_details
# --------------

@view_config(
     route_name='output_details',
     renderer='templates/output_details.pt',
     layout='default',
     permission='edit')
def output_details(request):
    title = u"Process Outputs"

    from .models import get_job
    job = get_job(request, uuid=request.params.get('uuid'))
    wps = WebProcessingService(job['service_url'], verbose=False)
    execution = WPSExecution(url=wps.url)
    execution.checkStatus(url=job['status_location'], sleepSecs=0)

    form_info="Status: %s" % (execution.status)
    
    return( dict(
        title=execution.process.title, 
        form_info=form_info,
        outputs=execution.processOutputs) )

# form
# -----

@view_config(
    route_name='execute',
    renderer='templates/form.pt',
    layout='default',
    permission='edit'
    )
class ExecuteView(FormView):
    log.debug('rendering execute')
    buttons = ('submit',)
    schema_factory = None
    wps = None
   
    def __call__(self):
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = WPSSchema
            
        try:
            session = self.request.session
            identifier = session['phoenix.process.identifier']
            self.wps = WebProcessingService(wps_url(self.request), verbose=False)
            process = self.wps.describeprocess(identifier)
            self.schema = self.schema_factory(
                info = True,
                title = process.title,
                process = process)
        except:
            raise
       
        return super(ExecuteView, self).__call__()

    def appstruct(self):
        return None

    def submit_success(self, appstruct):
        session = self.request.session
        identifier = session['phoenix.process.identifier']
        params = self.schema.serialize(appstruct)
      
        execution = execute_wps(self.wps, identifier, params)

        from .models import add_job
        add_job(
            request = self.request, 
            user_id = authenticated_userid(self.request), 
            identifier = identifier, 
            wps_url = self.wps.url, 
            execution = execution,
            notes = params.get('info_notes', ''),
            tags = params.get('info_tags', ''))

        return HTTPFound(location=self.request.route_url('jobs'))

@view_config(
    route_name='monitor',
    renderer='templates/embedded.pt',
    layout='default',
    permission='admin'
    )
def monitor(request):
    log.debug('rendering monitor view')
    return dict(external_url=supervisor_url(request))

@view_config(
    route_name='tds',
    renderer='templates/embedded.pt',
    layout='default',
    permission='edit'
    )
def thredds(request):
    return dict(external_url=thredds_url(request))

@view_config(
    route_name='catalog_wps_add',
    renderer='templates/catalog.pt',
    layout='default',
    permission='edit',
    )
class CatalogAddWPSView(FormView):
    #form_info = "Hover your mouse over the widgets for description."
    schema = None
    schema_factory = None
    buttons = ('add',)
    title = u"Catalog"

    def __call__(self):
        csw = CatalogueServiceWeb(csw_url(self.request))
        csw.getrecords2(maxrecords=100)
        wps_list = []
        for rec_id in csw.records:
            rec = csw.records[rec_id]
            if rec.format == 'WPS':
                wps_list.append((rec.references[0]['url'], rec.title))

        from .schema import CatalogAddWPSSchema
        # build the schema if it does not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = CatalogAddWPSSchema
            self.schema = self.schema_factory(title='Catalog').bind(
                wps_list = wps_list,
                readonly = True)

        return super(CatalogAddWPSView, self).__call__()

    def appstruct(self):
        return {'current_wps' : wps_url(self.request)}

    def add_success(self, appstruct):
        serialized = self.schema.serialize(appstruct)
        url = serialized['new_wps']

        csw = CatalogueServiceWeb(csw_url(self.request))
        try:
            csw.harvest(url, 'http://www.opengis.net/wps/1.0.0')
        except:
            log.error("Could not add wps service to catalog: %s" % (url))
            #raise

        return HTTPFound(location=self.request.route_url('catalog_wps_add'))

@view_config(
    route_name='catalog_wps_select',
    renderer='templates/catalog.pt',
    layout='default',
    permission='edit',
    )
class CatalogSelectWPSView(FormView):
    schema = None
    schema_factory = None
    buttons = ('submit',)
    title = u"Catalog"

    def __call__(self):
        csw = CatalogueServiceWeb(csw_url(self.request))
        csw.getrecords2(maxrecords=100)
        wps_list = []
        for rec_id in csw.records:
            rec = csw.records[rec_id]
            if rec.format == 'WPS':
                wps_list.append((rec.references[0]['url'], rec.title))

        from .schema import CatalogSelectWPSSchema
        # build the schema if it not exist
        if self.schema is None:
            if self.schema_factory is None:
                self.schema_factory = CatalogSelectWPSSchema
            self.schema = self.schema_factory(title='Catalog').bind(wps_list = wps_list)

        return super(CatalogSelectWPSView, self).__call__()

    def appstruct(self):
        return {'active_wps' : wps_url(self.request)}

    def submit_success(self, appstruct):
        serialized = self.schema.serialize(appstruct)
        wps_id = serialized['active_wps']
        log.debug('wps_id = %s', wps_id)
        update_wps_url(self.request, wps_id)        

        return HTTPFound(location=self.request.route_url('processes'))

@view_config(
    route_name='admin_user_register',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserRegisterView(FormView):
    from .schema import AdminUserRegisterSchema
    
    schema = AdminUserRegisterSchema()
    buttons = ('register',)
    title = u"Register User"

    def appstruct(self):
        return {}

    def register_success(self, appstruct):
        from .models import register_user
        user = self.schema.serialize(appstruct)
        register_user(self.request,
                      user_id = user.get('email'),
                      name = user.get('name'),
                      organisation = user.get('organisation'),
                      notes = user.get('notes'))

        return HTTPFound(location=self.request.route_url('admin_user_register'))

@view_config(
    route_name='admin_user_unregister',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserUnregisterView(FormView):
    from .schema import AdminUserUnregisterSchema
    
    schema = AdminUserUnregisterSchema()
    buttons = ('unregister',)
    title = u"Unregister User"

    def unregister_success(self, appstruct):
        from .models import unregister_user
        user = self.schema.serialize(appstruct)
        unregister_user(self.request, user_id=user.get('user_id'))
        
        return HTTPFound(location=self.request.route_url('admin_user_unregister'))

@view_config(
    route_name='admin_user_activate',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserActivateView(FormView):
    from .schema import AdminUserActivateSchema
    
    schema = AdminUserActivateSchema()
    buttons = ('activate',)
    title = u"Activate Users"
    
    def activate_success(self, appstruct):
        from .models import activate_user
        user = self.schema.serialize(appstruct)
        activate_user(self.request, user_id=user.get('user_id'))

        return HTTPFound(location=self.request.route_url('admin_user_activate'))

@view_config(
    route_name='admin_user_deactivate',
    renderer='templates/admin.pt',
    layout='default',
    permission='edit',
    )
class AdminUserDeactivateView(FormView):
    from .schema import AdminUserDeactivateSchema
    
    schema = AdminUserDeactivateSchema()
    buttons = ('deactivate',)
    title = u"Deactivate Users"

    def deactivate_success(self, appstruct):
        from .models import deactivate_user
        user = self.schema.serialize(appstruct)
        deactivate_user(self.request, user_id=user.get('user_id'))

        return HTTPFound(location=self.request.route_url('admin_user_deactivate'))

@view_config(
    route_name='map',
    renderer='templates/map.pt',
    layout='default',
    permission='edit'
    )
def map(request):
    return dict()

@view_config(
    route_name='help',
    renderer='templates/embedded.pt',
    layout='default',
    permission='view'
    )
def help(request):
    log.debug('rendering help view')
    return dict(external_url='/docs')

