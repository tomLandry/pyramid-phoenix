from pyramid.view import view_config

from phoenix.views.wizard import Wizard
from phoenix.models import get_folders

class SwiftAccess(Wizard):
    def __init__(self, request):
        super(SwiftAccess, self).__init__(
            request, name='wizard_swift_access', title="Swift Cloud Access")
        self.process = request.wps.describeprocess(identifier='swift_download')
        self.description = None

    def schema(self):
        from phoenix.schema import SwiftAccessSchema
        user = self.get_user()
        storage_url = user.get('swift_storage_url')
        auth_token = user.get('swift_auth_token')
            
        return SwiftAccessSchema().bind(containers=get_folders(storage_url, auth_token))

    def next_success(self, appstruct):
        self.success(appstruct)
        container = appstruct['container']
        parts = container.split('/')
        container = parts[0]
        value = dict(container=container)
        if len(parts) > 1:
            prefix = '/'.join(parts[1:])
            value['prefix'] = prefix
        return self.next('wizard_done')
    
    @view_config(route_name='wizard_swift_access', renderer='phoenix:templates/wizard/default.pt')
    def view(self):
        return super(SwiftAccess, self).view()
    
