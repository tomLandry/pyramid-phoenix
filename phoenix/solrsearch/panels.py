from pyramid_layout.panel import panel_config

from .search import solr_search

import logging
logger = logging.getLogger(__name__)


def query_path(request):
    # TODO: this is dirty. solrsearch should be a widget or/and use jquery ajax requests.
    current_path = request.current_route_path()
    if current_path.startswith('/wizard'):
        q_path = 'wizard_solr'
    else:
        q_path = 'solrsearch'
    return q_path


@panel_config(name='solrsearch_script', renderer='templates/solrsearch/panels/script.pt')
def solrsearch_script(context, request):
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    return dict(query_path=query_path(request), query=query, page=page)


@panel_config(name='solrsearch', renderer='templates/solrsearch/panels/search.pt')
def solrsearch(context, request):
    query = request.params.get('q', '')
    page = int(request.params.get('page', '0'))
    category = request.params.get('category')
    source = request.params.get('source')
    tag = request.params.get('tag')

    logger.debug("solrsearch panel context %s", context)

    result = dict(query_path=query_path(request), query=query, page=page, category=category, selected_source=source)
    url = request.registry.settings.get('solr.url')
    result.update(solr_search(url=url, query=query, page=page, category=category, source=source, tag=tag))
    # request.session.flash("Solr service is not available.", queue='danger')
    return result
