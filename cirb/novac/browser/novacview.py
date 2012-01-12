# -*- coding: UTF-8 -*-
import os
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _

from cirb.novac.utils import *
from cirb.novac.browser.interfaces import INovacCustomization
import re, os, logging
import urllib2, socket
from urllib2 import URLError, HTTPError

LISTPRIVATE='listprivate'

class INovacView(INovacCustomization):
    """
    Cas view interface
    """


class NovacView(BrowserView):
    """
    Cas browser view
    """
    implements(INovacView)

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
            
        self.json_file = registry['cirb.novac.json_file']
            

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def view_name(self):
        return ""
    
    def second_level(self):
        return ""
    
    # also used by views who extends NovacView
    def utils_url(self):
        error = False
        msg_error = ""
        if not self.novac_url:
            error=True
            msg_error=_(u'No url for cirb.novac.novac_url')
        # depends of cirb.urbis eggs
        if not self.urbis_url:
            error=True
            msg_error=_(u'No url for cirb.urbis.urbis_url')
        if not self.urbis_cache_url:
            error=True
            msg_error=_(u'No url for cirb.urbis.urbis_cache_url')
        if not self.json_file:
            error=True
            msg_error=_(u'No json_file') 
            
        return {'novac_url':self.novac_url, 
                'urbis_url':self.urbis_url,
                'urbis_cache_url':self.urbis_cache_url,
                'rest_service':self.rest_service,
                'json_file':self.json_file,
                'error':error,
                'msg_error':msg_error}
          
    def novac(self):
        """
        novac method
        """
        error=False
        msg_error=''        
        return {'private_url':LISTPRIVATE}
   
