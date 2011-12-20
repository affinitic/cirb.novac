# -*- coding: UTF-8 -*-
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
        self.novac_url = registry['cirb.novac.novac_url']
        self.urbis_url = registry['cirb.urbis.urbis_url']
        self.urbis_cache_url = registry['cirb.urbis.urbis_cache_url']
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
    
    def wfs_request(self):
        query_string = self.request.environ['QUERY_STRING']
        url = query_string.replace("url=","")
        #url = self.request.form.get('url')
        #headers = {'User-Agent': 'Novac/1 +http://www.urbanisme.irisnet.be/'}
        return called_url(url , [{'Content-Type':'text/html'}, {'lang':self.context.Language()}], lang=self.context.Language())

    def wfs_post_request(self):
        query_string = self.request.environ['QUERY_STRING']
        #url = query_string.replace("url=","")
        url = self.request.form.get('url')
        jsonheader = self.request.form.get('json')
        lang = self.request.form.get('language')
        street = self.request.form.get('street')
        post_code = self.request.form.get('postcode')
        number = self.request.form.get('number')
        
        header=[]
        header.append({"Content-Type":"application/x-www-form-urlencoded"})
        if jsonheader:
            header=[]
            header.append({"Content-Type":"application/json"})
            header.append({"ACCEPT":"application/json"})
        params = {}
        data = None
        params['language'] = lang
        params['address'] = {'street':{'name':street, 'postcode':post_code}, 'number':number}
        import json
        try:
            data = json.dumps(params)
        except ValueError, e:
            self.logger.error('Json value error : %s.' % e.message)
        except SyntaxError, e:
            self.logger.error('Json bad formatted : %s.' % e.message)
        return call_post_url(url , header, data)



