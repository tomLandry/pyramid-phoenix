import colander
from deform.widget import RadioChoiceWidget

from pyramid.view import view_config

from owslib.wps import WebProcessingService

from phoenix.wizard.views import Wizard

SOURCE_TYPES = {
    'wizard_esgf_search': "Earth System Grid (ESGF)",
    # 'wizard_swift_login': "Swift Cloud",
    'wizard_threddsservice': "Thredds Catalog Service",
    # 'wizard_upload': "Local Storage",
    'wizard_solr': "Birdhouse Solr Search"
    }


class SourceSchemaNode(colander.SchemaNode):
    schema_type = colander.String
    widget = None

    def after_bind(self, node, kw):
        values = SOURCE_TYPES.items()
        if not kw['request'].solr_activated:
            values.remove(('wizard_solr', SOURCE_TYPES['wizard_solr']))
        self.widget = RadioChoiceWidget(values=values)


class Schema(colander.MappingSchema):
    source = SourceSchemaNode()


class ChooseSource(Wizard):
    def __init__(self, request):
        super(ChooseSource, self).__init__(
            request, name='wizard_source', title="Choose Data Source")
        wps = WebProcessingService(
            url=request.route_url('owsproxy', service_name=self.wizard_state.get('wizard_wps')['identifier']),
            verify=False, skip_caps=True)
        process = wps.describeprocess(self.wizard_state.get('wizard_process')['identifier'])
        for data_input in process.dataInputs:
            if data_input.identifier == self.wizard_state.get('wizard_complex_inputs')['identifier']:
                self.title = "Choose Data Source for %s" % data_input.title
                break
        # self.description = self.wizard_state.get('wizard_complex_inputs')['identifier']

    def breadcrumbs(self):
        breadcrumbs = super(ChooseSource, self).breadcrumbs()
        breadcrumbs.append(dict(route_path=self.request.route_path(self.name), title=self.title))
        return breadcrumbs
        
    def schema(self):
        return Schema().bind(request=self.request)

    def next_success(self, appstruct):
        self.success(appstruct)
        return self.next( appstruct.get('source') )
        
    @view_config(route_name='wizard_source', renderer='../templates/wizard/default.pt')
    def view(self):
        return super(ChooseSource, self).view()
