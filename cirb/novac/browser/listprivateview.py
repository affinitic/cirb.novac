from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

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
        registry = getUtility(IRegistry)
        novac_url = registry['cirb.novac.novac_url']
        error=False
        msg_error=''
        if not novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        user = self.portal_state.member()
        return {'novac_url':novac_url,'error':error,'msg_error':msg_error, 'user':user}
    