from pyramid.view import view_config, view_defaults
from pyramid.httpexceptions import HTTPFound

from phoenix.utils import ActionButton

import logging
logger = logging.getLogger(__name__)

@view_defaults(permission='submit')
class NodeActions(object):
    """Actions related to job monitor."""

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.session = self.request.session
        self.flash = self.request.session.flash
        self.db = self.request.db.jobs

    def _selected_children(self):
        """
        Get the selected children of the given context.

        :result: List with select children.
        :rtype: list
        """
        ids = self.session.pop('phoenix.selected-children')
        self.session.changed()
        return ids

    @view_config(route_name='delete_job')
    def delete_job(self):
        job_id = self.request.matchdict.get('job_id')
        logger.debug("jobid: %s", job_id)
        # TODO: check permission ... either admin or owner.
        self.db.delete_one({'identifier': job_id})
        self.flash("Job {0} deleted.".format(job_id), queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))


    @view_config(route_name='delete_jobs')
    def delete_jobs(self):
        """
        Delete selected jobs.
        """
        ids = self._selected_children()
        if ids is not None:
            self.db.delete_many({'identifier': {'$in': ids} })
            self.flash(u"Selected jobs were deleted.", queue='info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='make_public')
    def make_public(self):
        """
        Make selected jobs public.
        """
        ids = self._selected_children()
        if ids is not None:
            self.db.update_many({'identifier':  {'$in': ids}}, {'$set': {'is_public': True}})
            self.flash(u"Selected jobs were made public.", 'info')
        return HTTPFound(location=self.request.route_path('monitor'))

    @view_config(route_name='make_private')
    def make_private(self):
        """
        Make selected jobs private.
        """
        ids = self._selected_children()
        if ids is not None:
            self.db.update_many({'identifier':  {'$in': ids}}, {'$set': {'is_public': False}})
            self.flash(u"Selected jobs were made private.", 'info')
        return HTTPFound(location=self.request.route_path('monitor'))


def monitor_buttons(context, request):
    """
    Build the action buttons for the monitor view based on the current
    state and the persmissions of the user.

    :result: List of ActionButtons.
    :rtype: list
    """
    buttons = []
    buttons.append(ActionButton('delete_jobs', title=u'Delete',
                                css_class=u'btn btn-danger'))
    buttons.append(ActionButton('make_public', title=u'Make Public'))
    buttons.append(ActionButton('make_private', title=u'Make Private'))
    return [button for button in buttons if button.permitted(context, request)]

def includeme(config):
    """ Pyramid includeme hook.

    :param config: app config
    :type config: :class:`pyramid.config.Configurator`
    """

    config.add_route('delete_job', 'delete_job/{job_id}')
    config.add_route('delete_jobs', 'delete_jobs')
    config.add_route('make_public', 'make_public')
    config.add_route('make_private', 'make_private')
