# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

class Happy(BrowserView):
    """
    happy pag browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.logger = logging.getLogger('cirb.novac.browser.novacview')
        registry = getUtility(IRegistry)
        novac_url = os.environ.get("novac_url", None)
        if novac_url:
            self.novac_url = novac_url
        else:
            self.novac_url = registry['cirb.novac.novac_url']
        
        urbis_url = os.environ.get("urbis_url", None)
        if urbis_url:
            self.urbis_url = urbis_url
        else:
            self.urbis_url = registry['cirb.urbis.urbis_url']
            
        urbis_cache_url = os.environ.get("urbis_cache_url", None)
        if urbis_cache_url:
            self.urbis_cache_url = urbis_cache_url
        else:
            self.urbis_cache_url = registry['cirb.urbis.urbis_cache_url']
        
        rest_service = os.environ.get("rest_service", None)
        if rest_service:
            self.rest_service = rest_service
        else:
            self.rest_service = registry['cirb.novac.rest_service']        
    
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def happy(self):
        results={}
        results['sso'] = self.get_sso()
        results['waws'] = self.get_waws()
        results['urbis'] = self.get_urbis()        
        return results
    
    def get_sso(self):
        return "sso"
    
    def get_waws(self):
        return "waws"
    
    def get_urbis(self):
        return "urbis"    
    
    