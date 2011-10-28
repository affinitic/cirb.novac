# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _

PRIVATE_FODLER_WS = '/nova/sso/dossiers/150000?errn=errn3' # ?errn=errn3 used to test
HISTORY =  '/nova/sso/dossiers/150000/history?errn=errn3' # ?errn=errn3 used to test

class IPrivateView(Interface):
    """
    Cas view interface
    """



class PrivateView(BrowserView):
    """
    Cas browser view
    """
    implements(IPrivateView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def private(self):
        
        registry = getUtility(IRegistry)
        novac_url = registry['cirb.novac.novac_url']
        error=False
        msg_error=''
        if not novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        return {'novac_url':novac_url,'error':error,'msg_error':msg_error}
    