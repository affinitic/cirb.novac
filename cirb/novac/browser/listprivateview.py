from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from cirb.novac import novacMessageFactory as _


class IListprivateView(Interface):
    """
    Cas view interface
    """

    def test():
        """ test method"""


class ListprivateView(BrowserView):
    """
    Cas browser view
    """
    implements(IListprivateView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def listprivate(self):
        ws_waws = ''
        if self.context.getPortalTypeName() == 'List Private Folder':
            ws_waws = self.context.getWs_url()
            
        if not ws_waws:
            return {'error':True, 'error_text': 'Add a List Private Folder'}
        return {'error':False, 'ws_waws':ws_waws}
    