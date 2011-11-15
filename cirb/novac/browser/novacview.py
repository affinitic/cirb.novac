# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _

from cirb.novac.utils import *

import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError


class INovacView(Interface):
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

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def view_name(self):
        return "novac"
    
    def novac(self):
        """
        novac method
        """
        registry = getUtility(IRegistry)
        novac_url = registry['cirb.novac.novac_url']
        urbis_url = registry['cirb.urbis.urbis_url']
        urbis_cache_url = registry['cirb.urbis.urbis_cache_url']
        json_file = registry['cirb.novac.json_file']
        error=False
        msg_error=''
        if not novac_url:
            error=True
            msg_error=_(u'No url for cirb.novac.novac_url')
        if not urbis_url:
            error=True
            msg_error=_(u'No url for cirb.urbis.urbis_url')
        if not json_file:
            error=True
            msg_error=_(u'No json_file')
        private_url='wawslistprivate_view'
        return {'novac_url':novac_url,
                'urbis_url':urbis_url,
                'urbis_cache_url':urbis_cache_url,
                'json_file':json_file,
                'private_url':private_url,'error':error,'msg_error':msg_error}
    
    def wfs_request(self):        
        query_string = self.request.environ['QUERY_STRING']
        url = query_string.replace("url=","")
        #url = self.request.form.get('url')
        #headers = {'User-Agent': 'Novac/1 +http://www.urbanisme.irisnet.be/'}
        return called_url(url , [{'Content-Type':'text/html'}])

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
       
        params['language'] = lang
        params['address'] = {'street':{'name':street, 'postcode':post_code}, 'number':number}
        import json
        data = json.dumps(params)
        return call_post_url(url , header, data)



