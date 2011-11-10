# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError

from cirb.novac import novacMessageFactory as _

from cirb.novac.browser.novacview import INovacView, NovacView
from cirb.novac.utils import *

PUB_DOSSIER = 'nova/pub/dossiers'

class IPublicView(Interface):
    """
    Cas view interface
    """


class PublicView(BrowserView):
    """
    Cas browser view
    """
    implements(IPublicView)
    
    novac_url=''
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.novac_url = registry['cirb.novac.novac_url']
        self.urbis_url = registry['cirb.urbis.urbis_url']
        self.rest_service = registry['cirb.novac.rest_service']
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def view_name(self):
        return "public"
        
    def public(self):
        folder_id = self.request.form.get('id')
        error=False
        msg_error=''
        if not self.novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        if not folder_id:
            error=True
            msg_error=_(u'No folder id')
        
        return {'novac_url':self.novac_url,'urbis_url':self.urbis_url ,'folder_id':folder_id,'error':error,'msg_error':msg_error}
        
    
    def python_json(self):
        oldtimeout = socket.getdefaulttimeout()
        data = ''
        msg_error=''
        error=False
        try:
            num_dossier = self.request.form.get('id')
        except:
            error = True
            msg_error = 'Not num_dossier in url (GET)'
        url = '%s/%s/%s/' % (self.novac_url, PUB_DOSSIER, num_dossier)
        #TODO use utils method
        #
        try:
            socket.setdefaulttimeout(7) # let's wait 7 sec            
            
            request = urllib2.Request(url,headers={'content-type': 'application/json', 
                                                   'ACCEPT': 'application/json'})            
            #request.add_header('User-Agent', 'Cas/1 +http://www.cirb.irisnet.be/')
            opener = urllib2.build_opener()
            data_from_url = opener.open(request).read()
        except HTTPError, e:
            msg_error = _('The server couldn\'t fulfill the request.<br />Error code: %s' % e.code)
            error=True
            return {'data':data, 'error':error, 'msg_error':msg_error, 'called_url':url}
        except URLError, e:
            msg_error = _('We failed to reach a server.<br /> Reason: %s'% e.reason)
            error=True
            return {'data':data, 'error':error, 'msg_error':msg_error, 'called_url':url}
        finally:
            socket.setdefaulttimeout(oldtimeout)
        
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        
        import json
        data = json.loads(data_from_url)
        try:
            geometry = data['geometry']
            properties = data['properties']
        except:
            geometry=None
            properties=None
        try:
            address = '%s, %s %s %s' % (properties['numberFrom'],
                                    properties['streetName'],
                                    properties['zipCode'],
                                    properties['municipality'],)
        except:
            address = not_avaiable   
            
        type_dossier = get_properties(self.context, properties,"typeDossier")
        desc = get_properties(self.context, properties,'object')
        ref = get_properties(self.context, properties,'novaRef')
        folder_filed = get_properties(self.context, properties,'folderFiled')
        introduce_on = get_properties(self.context, properties,'startPublicInquiry')
        lang = get_properties(self.context, properties,'lang')
        status = get_properties(self.context, properties,'statusPermit')
       
        try:
            x = str(geometry['x'])
            y = str(geometry['y'])
        except:
            x = '150000.0'
            y = '170000.0'
            
        results = {'address':address, 'type_dossier':type_dossier,'desc':desc,'ref':ref, 
                 'num_dossier':num_dossier, 'folder_filed':folder_filed, 'introduce_on':introduce_on,
                 'lang':lang, 'status':status, 'x':x, 'y':y}
        
        return {'data':data, 'rest_service':self.rest_service, 'results':results,
                'error':error, 'msg_error':msg_error, 'called_url':url }
    
    
        