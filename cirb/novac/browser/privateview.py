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
        dossier_url = '%s%s%s' % (self.novac_url,PRIVATE_FODLER_WS,dossier_id)
        jsondata = called_url(dossier_url, 'application/json')
        
        history_url = '%s%s' % (dossier_url,HISTORY)
        history = called_url(history_url, 'application/json')
        
        
        import json
        properties = json.loads(jsondata)
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        try:
            address = '%s, %s %s %s' % (properties['numberFrom'],
                                    properties['streetName'],
                                    properties['zipcode'],
                                    properties['municipality'],)
        except:
            address = not_avaiable   
        
        results={}
        results['type_dossier'] = get_properties(self.context, properties,"typeDossier")
        results['municipality_owner'] = get_properties(self.context, properties,"municipalityOwner")
        results['dossier_id'] = get_properties(self.context, properties,"id")
        results['lang'] = get_properties(self.context, properties,"languageRequest")
        results['manager'] = get_properties(self.context, properties,"manager")
        results['desc'] = get_properties(self.context, properties,'object')
        results['ref'] = get_properties(self.context, properties,'refNova')
        results['point_cc'] = get_properties(self.context, properties,'pointCC')
        results['public_inquiry'] = get_properties(self.context, properties,'publicInquiry')
        results['specific_reference'] = get_properties(self.context, properties,'specificReference')
     
        
        return {'novac_url':self.novac_url,'error':error,'msg_error':msg_error,
                'jsondata':jsondata, 'history':history, 'results':results}
    