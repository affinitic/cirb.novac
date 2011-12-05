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
import logging

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
        logger = logging.getLogger('cirb.novac.browser.publicview.python_json')
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
        data_from_url = called_url(url, [{'Content-Type': 'application/json'},{'ACCEPT': 'application/json'}, {'lang':self.context.Language()}], lang=self.context.Language())
        logger.info(self.context.Language())
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        if data_from_url:
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
    
            table_ids = ["id","novaRef","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","dateNotifDecision",
                         "dateDeadline","municipalityOwner","specificReference"]
            results = {}
            results['address'] = address
            results['num_dossier'] = num_dossier
            for t in table_ids:
                results[t] =  get_properties(self.context, properties, t)
            try:
                results['x'] = str(geometry['x'])
                results['y'] = str(geometry['y'])
            except:
                results['x']  = '150000.0'
                results['y']  = '170000.0'
                
        else:
            error = True
            msg_error = 'Num dossier %s is unknown or empty' %num_dossier
            return  {'error':error, 'msg_error':msg_error, 'called_url':url}
        return {'data':data, 'rest_service':self.rest_service, 'results':results,
                'error':error, 'msg_error':msg_error, 'called_url':url }
    
    
        