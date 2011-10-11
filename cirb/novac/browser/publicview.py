from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from cirb.novac import novacMessageFactory as _


class IPublicView(Interface):
    """
    Cas view interface
    """

    def test():
        """ test method"""


class PublicView(BrowserView):
    """
    Cas browser view
    """
    implements(IPublicView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def public(self):
        ws_waws = ''
        for elem in self.context.contentValues():
            if elem.getPortalTypeName() == 'Public Folder':
                ws_waws = elem.getWs_url()    
        if not ws_waws:
            return {'error':True, 'error_text': 'Add a Public Folder'}
        return {'error':False,'ws_waws':ws_waws}
    