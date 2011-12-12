# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.utils import *
from cirb.novac.browser.novacview import INovacView, NovacView

import logging
import urllib
logger = logging.getLogger('cirb.novac.browser.privateview')
PRIVATE_FODLER_WS = '/nova/sso/dossiers/' # ?errn=errn3 used to test
HISTORY =  '/history' # ?errn=errn3 used to test
SECONDARY_KEYS = '/waws/sso/ssks/distributed?targetID='
ADD_SECONDARY_KEY = '/waws/sso/ssks?targetID='
ADD_SECONDARY_KEY_NAME = '&keyName='
REVOKE_SECONDARY_KEY = '/waws/sso/ssks/revoke?key='

class IPrivateView(INovacView):
    """
    Cas view interface
    """


class PrivateView(NovacView):
    """
    Cas browser view
    """
    implements(IPrivateView)
    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        self.novac_url = registry['cirb.novac.novac_url']
        self.urbis_url = registry['cirb.urbis.urbis_url']
        self.id_dossier = self.request.form.get('id')
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def view_name(self):
        return "Private"
    
    def second_level(self):
        return "Listprivate"
    
    def private(self):        
        error=False
        msg_error=''
        if not self.novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        elif not self.id_dossier:
            error=True
            msg_error=_(u'No id folder in get method')
        #dossier_id = self.request.form.get('id')
        dossier_url = '%s%s%s' % (self.novac_url,PRIVATE_FODLER_WS,self.id_dossier)
        user = get_user(self.request)
        jsondata = called_url(dossier_url, [{'Content-Type':'application/json'},{'ACCEPT':'application/json'}, {'RNHEAD':user['id']}, {'lang':self.context.Language()}], lang=self.context.Language())
        if not jsondata:
            logger.info('Not able to call ws %s' % dossier_url)
            error=True
            msg_error=_(u'Not able to call ws')
            return {'novac_url':self.novac_url, 'urbis_url':self.urbis_url, 'error':error,'msg_error':msg_error}
        history_url = '%s%s' % (dossier_url,HISTORY)
        history = called_url(history_url,[{'Content-Type':'application/json'}, {'ACCEPT':'application/json'}, {'RNHEAD':user['id']}, {'lang':self.context.Language()}], lang=self.context.Language())
        if not history:
            logger.info('Not able to call ws %s' % history_url)
            error=True
            msg_error=_(u'Not able to call ws')
            return {'novac_url':self.novac_url, 'urbis_url':self.urbis_url, 'error':error,'msg_error':msg_error}
        
        import json
        properties = json.loads(jsondata)
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        results={}
        try:
            results['address'] = '%s, %s %s %s' % (properties['numberFrom'],
                                    properties['streetName'],
                                    properties['zipcode'],
                                    properties['municipality'],)
        except:
            results['address'] = not_avaiable   
        
        # in public novaRef instead of refNova
        table_ids = ["id","refNova","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","dateNotifDecision",
                         "dateDeadline","municipalityOwner","specificReference", 
                         "manager", "isOwner", "x", "y"]
        
        for t in table_ids:
            results[t] =  get_properties(self.context, properties, t)
        
        
        h_prop = json.loads(history)
        h_res = []
        for prop in h_prop:
            from datetime import datetime
            d = datetime.fromtimestamp(float(get_properties(self.context, prop,"consultationDate"))/1000)
            consultationDate = d.strftime("%d/%m/%y %H:%M")
            keyName = get_properties(self.context, prop,"keyName")
            h_res.append({'consultationDate':consultationDate, 'keyName':keyName})
            
        
        
        return {'novac_url':self.novac_url, 'urbis_url':self.urbis_url, 'error':error,'msg_error':msg_error,
                'jsondata':jsondata, 'history':history, 'results':results, 'h_res':h_res}
    
    def activate_mandat(self):
        mandat = urllib.quote(self.request.form.get('mandat'))
        targetID = urllib.quote(self.request.form.get('targetID'))
        query_string = self.request.environ['QUERY_STRING']
        activate_mandat = '%s%s%s%s%s' %(self.novac_url,ADD_SECONDARY_KEY,targetID,
                                     ADD_SECONDARY_KEY_NAME,mandat)
        
        results = call_put_url(activate_mandat,[{'Content-Type':'application/xml'}], query_string)
        
        return results

    def revoke_mandat(self):
        #key = self.request.form.get('key')
        query_string = self.request.environ['QUERY_STRING']
        key = urllib.quote(self.request.form.get('key'))
        revoke_mandat = '%s%s%s' %(self.novac_url,REVOKE_SECONDARY_KEY,key)        
        results = call_put_url(revoke_mandat,[{'Content-Type':'application/xml'}], query_string)
        
        return results
    
    def get_table_lines_secondary_keys(self):
        if self.id_dossier:
            targetID = self.id_dossier
        else:
            targetID = urllib.quote(self.request.form.get('targetID'))
                
        secondary_keys_url = '%s%s%s' %(self.novac_url,SECONDARY_KEYS,targetID)
        user = get_user(self.request)
        secondary_keys = called_url(secondary_keys_url, [{'Content-Type':'application/json'}, {'ACCEPT':'application/json'},{'RNHEAD':user['id']}, {'lang':self.context.Language()}], lang=self.context.Language())
        if not secondary_keys:
            return '<tr class="secondary_key" style="height: 0px;"><td></td><td></td><td></td></tr>'
        results=[]
        import json
        jsondatas = json.loads(secondary_keys)
        
        table = ''
        for properties in jsondatas:
            result={}
            result['keyName'] = get_properties(self.context, properties,"keyName")
            result['key'] = get_properties(self.context, properties,"key")
          
            results.append(result)
            formatted_key = ''
            for i in range(len(result['key'])):
                if i % 4 == 0 and i != 0:
                    formatted_key += " - "                
                formatted_key += result['key'][i]

            table+='''
            <tr class="secondary_key">
            <td>%s</td>
            <td>%s</td>
            <td><a href="%s/revoke_mandat?key=%s" class="revoke_mandat">revoke</a></td>
            </tr>''' % (result['keyName'], formatted_key, 
                        self.context.absolute_url(), urllib.quote(result['key']))
       
        return table
