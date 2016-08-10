import json

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView


class ManagedStorageView(BikaListingView):
    """This is the default view for Managed storage.
    """
    template = ViewPageTemplateFile("managedstorage_view.pt")

    def __init__(self, context, request):
        super(ManagedStorageView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        self.positions = self.context.objectValues('StoragePosition')
        self.title = self.context.title
        self.icon = self.portal_url + "/++resource++bika.lims.images/" \
                    + "managedstorage_big.png"

        StoragePositions = StoragePositionsView(self.context, self.request)
        self.positions_table = StoragePositions.contents_table(table_only=True)

        StorageGraph = StorageGraphView(self.context, self.request)
        self.graph = StorageGraph()

        return self.template()


class StoragePositionsView(BikaListingView):
    """This is the listing that shows Storage Positions at this location.
    """

    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(StoragePositionsView, self).__init__(context, request)
        self.context = context
        self.request = request
        self.catalog = 'bika_setup_catalog'
        path = '/'.join(context.getPhysicalPath())
        self.contentFilter = {'portal_type': 'StoragePosition',
                              'sort_on': 'sortable_title',
                              'path': {'query': path, 'depth': 1, 'level': 0}
                              }
        self.context_actions = {}
        self.title = ''
        self.description = ''
        self.icon = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.columns = {
            'id': {'title': _('ID'), 'index': 'id'},
            'StorageTypes': {'title': _('Storage Types'), 'toggle': True},
            'StoredItem': {'title': _('Stored Item'), 'toggle': True},
            'review_state': {'title': _('State'), 'toggle': True},
        }
        self.review_states = [
            {'id': 'default',
             'title': _('Active'),
             'contentFilter': {'inactive_state': 'active'},
             'transitions': [{'id': 'deactivate'}, ],
             'columns': ['id',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
            {'id': 'all',
             'title': _('All'),
             'contentFilter': {},
             'columns': ['id',
                         'StorageTypes',
                         'StoredItem',
                         'review_state']},
        ]

    def folderitem(self, obj, item, index):
        workflow = getToolByName(self.context, "portal_workflow")
        mtool = getToolByName(self.context, 'portal_membership')
        if not item.has_key('obj'):
            return item
        obj = item['obj']

        item['id'] = obj.getHierarchy()

        storage_titles = [s['title'] for s in obj.getStorageTypes()]
        item['StorageTypes'] = ','.join(storage_titles)

        si = obj.getStoredItem()
        item['StoredItem'] = si.Title() if si else ''

        return item


class StorageGraphView(BrowserView):
    """Show graphic layout of available and occupied positions.
    """
    template = ViewPageTemplateFile("managedstorage_graph.pt")
    title = _("Managed storage positions")

    def __init__(self, context, request):
        super(StorageGraphView, self).__init__(context, request)
        self.context = context
        self.request = request

    def __call__(self):
        return self.template()


class PositionsInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        response = {}
        workflow = getToolByName(self.context, 'portal_workflow')
        positions = []
        response = {'x': self.context.getXAxis(),
                    'y': self.context.getYAxis(),
                    'n': self.context.getZAxis()}

        children = self.context.getPositions()
        for Position in children:
            aid, name, subject, volume, path, pos = '', '', 0, 0, '', ''
            if not Position.available():
                import pdb;pdb.set_trace()
                sample = Position.getSample()
                aid = sample.getId()
                name = sample.Title()
                volume = sample.getVolume()
                path = sample.absolute_url_path()
                pos = Position.absolute_url_path()

            state = workflow.getInfoFor(Position, 'review_state')
            positions.append({
                'occupied': state == 'occupied',
                'reserved': state == 'reserved',
                'address': Position.Title(),
                'state': state,
                'aid': aid,
                'name': name,
                'subject': subject,
                'volume': volume,
                'path': path,
                'pos': pos
            })
            response['positions'] = positions

        return json.dumps(response)


class SampleInfo:
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.errors = {}

    def __call__(self):
        form = self.request.form
        id = form['position']
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        brains = catalog.searchResults(portal_type="StorageLocation", id=id)
        sample = brains[0].getObject().getSample()

        ret = {
            'id': sample.getId(),
            'name': sample.Title(),
            'quantity': sample.getQuantity(),
            'volume': sample.getVolume(),
            'path': sample.absolute_url_path()
        }

        return json.dumps(ret)
