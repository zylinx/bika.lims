from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface import implements

from bika.lims.browser.multifile import MultifileView
from bika.lims import bikaMessageFactory as _


class ProductMultifileView(MultifileView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(ProductMultifileView, self).__init__(context, request)
        self.show_workflow_action_buttons = False
        self.title = self.context.translate(_("Product Files"))
        self.description = "Different interesting documents and files to be attached to the product"