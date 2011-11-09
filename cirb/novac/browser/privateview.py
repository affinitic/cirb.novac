# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.utils import *

PRIVATE_FODLER_WS = '/nova/sso/dossiers/' # ?errn=errn3 used to test
HISTORY =  '/history' # ?errn=errn3 used to test

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
        registry = getUtility(IRegistry)
        self.novac_url = registry['cirb.novac.novac_url']
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def private(self):        
        error=False
        msg_error=''
        if not self.novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        dossier_id = self.request.form.get('id')
        dossier_url = '%s%s%s' %(self.novac_url,PRIVATE_FODLER_WS,dossier_id)
        dossier = called_url(dossier_url, 'application/json')
        
        return {'novac_url':self.novac_url,'error':error,'msg_error':msg_error,
                'data':dossier}
    