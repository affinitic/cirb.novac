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
import json

from cirb.novac.browser.novacview import INovacView, NovacView
from cirb.novac.utils import *
from cirb.novac.browser.interfaces import INovacCustomization

PUB_DOSSIER = 'nova/pub/dossiers'

class IPublicView(INovacView):
    """
    Cas view interface
    """


class PublicView(NovacView):
    """
    Cas browser view
    """
    implements(IPublicView)
    
    
    def __init__(self, context, request):
        super(PublicView, self).__init__(context, request)
        self.logger = logging.getLogger('cirb.novac.browser.publicview')
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def view_name(self):
        return _(u"Public")    
    
    def public_error(self, msg_error):
        self.logger.error(msg_error)        
        return {"error":True, "msg_error":msg_error}
    
    def public(self):
        error = False
        try:
            num_dossier = self.request.form.get('id')
        except:
            msg_error = u'Not num_dossier in url (GET)'
            return self.public_error(msg_error)
        
        url = '%s/%s/%s/' % (self.novac_url, PUB_DOSSIER, num_dossier)
        
        json_from_ws = self.call_ws(url)
        if not json_from_ws:
            msg_error = _(u'Not able to call this dossier : %s' % url)
            return self.public_error(msg_error)
        
        jsondata = json_processing(json_from_ws)
        if not jsondata:
            msg_error = _(u'Not able to read this json : %s' % jsondata)
            return self.public_error(msg_error)
        
        results = self.dossier_processing(jsondata)
        #data and celled_url used for test
        return {'data':jsondata, 'results':results,'error':error,'called_url':url}
    
    
    def call_ws(self, url):
        headers = [{'Content-Type':'application/json'},{'ACCEPT':'application/json'}, {'Accept-Language':'%s-be' % self.context.Language()}]
        return called_url(url, headers)
    
    def dossier_processing(self, jsondata):
        msgid = _(u"not_available")
        not_available = self.context.translate(msgid)
        
        table_ids = ["id","novaRef","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","dateNotifDecision",
                         "dateDeadline","municipalityOwner","specificReference"]
        
        geometry = jsondata.get('geometry', None)
        if geometry:
            geo_results = Dossier(geometry, ["x","y"], not_available, has_address=False)
        else:
            self.logger.error("public url return a no excpected json, no 'geometry' parameter")        
        
        dossier = jsondata.get('properties', None)
        if dossier:
            dos_results = Dossier(dossier, table_ids, not_available, has_address=True)
        else:
            self.logger.error("public url return a no excpected json, no 'properties' parameter")
        
        return dict(dos_results.items() + geo_results.items())   
    
        