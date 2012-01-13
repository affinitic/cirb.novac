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
        novac_url = os.environ.get("novac_url", None)
        if novac_url:
            self.novac_url = novac_url
        else:
            registry = getUtility(IRegistry)
            self.novac_url = registry['cirb.novac.novac_url']        
        
            

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
            
        return {'novac_url':self.novac_url,              
                'error':error,
                'msg_error':msg_error}
          
    def novac(self):
        """
        novac method
        """
        error=False
        msg_error=''        
        return {'private_url':LISTPRIVATE}
   
