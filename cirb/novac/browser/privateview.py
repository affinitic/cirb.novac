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
        super(PrivateView, self).__init__(context, request)
        self.logger = logging.getLogger('cirb.novac.browser.privatecview')
        self.id_dossier = self.request.form.get('id')
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def view_name(self):
        return _(u"Private")
    
    def second_level(self):
        return _(u"Listprivate")

    def private_error(self, msg_error):
        return {'error':True,'msg_error':msg_error}
    
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
        dossier_url = '%s%s%s' % (self.novac_url, PRIVATE_FODLER_WS, self.id_dossier)        
     
        json_from_ws = self.called_ws(dossier_url)
        if not json_from_ws:
            self.logger.error = ('Not able to call ws %s' % dossier_url)
            msg_error = _(u'Not able to call ws')
            return self.private_error(msg_error)
        
        jsondata = json_processing(json_from_ws)
        if not jsondata:
            msg_error = _(u'Not able to read this json : %s' % jsondata)
            return self.private_error(msg_error)
        
        results = self.dossier_processing(jsondata)
        
        # Historic of dossier
        history_url = '%s%s' % (dossier_url, HISTORY)
        history = self.called_ws(history_url)
        if not history:
            self.logger.info('Not able to call ws %s' % history_url)
            msg_error = _(u'Not able to call ws')
            return self.private_error(msg_error)
        
        jsonhistory = json_processing(history)
        if not jsonhistory:
            msg_error = _(u'Not able to read this json : %s' % jsonhistory)
            return self.private_error(msg_error)
        
        history_ids = ['consultationDate','keyName']
        historys = update_dossiers(jsonhistory, history_ids, "not_available", has_address=False)
        h_res = self.formated_history_date(historys)
        user = get_user(self.request, self.context)
        if not user:
            msg_error = _('User undefined.')
            return self.listprivate_error(msg_error)
        results['user'] = user['name']        
        results['jsondata'] = jsondata
        results['jsonhistory'] = jsonhistory
        results['error'] = False
        results['h_res'] = h_res
        return results
    
    def dossier_processing(self, jsondata):
        msgid = _(u"not_available")
        not_available = self.context.translate(msgid)
        
        # in public novaRef instead of refNova
        table_ids = ["id","refNova","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","dateNotifDecision",
                         "dateDeadline","municipalityOwner","specificReference", 
                         "manager", "isOwner", "x", "y"]
        
        return Dossier(jsondata, table_ids, not_available, has_address=True)
             
    def formated_history_date(self, historys):
        h_res = []
        for history in historys:
            from datetime import datetime
            d = datetime.fromtimestamp(float(history["consultationDate"])/1000)
            history['consultationDate'] = d.strftime("%d/%m/%y %H:%M")
            h_res.append(history)
        return h_res
    
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
        secondary_keys = self.called_ws(secondary_keys_url)
        
        empty_table = '<tr class="secondary_key" style="height: 0px;"><td></td><td></td><td></td></tr>'
        if not secondary_keys:
            return empty_table
        
        jsondata = json_processing(secondary_keys)
        if not jsondata:
            return empty_table
                
        keys = self.secondarykeys_processing(jsondata)
        formatted_keys = self.generate_formatted_keys(keys)
          
        return make_table_rows(self.context.absolute_url(), formatted_keys)
    
    def called_ws(self, url):
        user = get_user(self.request)
        headers = [{'Content-Type':'application/json'},{'ACCEPT':'application/json'}, {'RNHEAD':user['id']}, {'Accept-Language':'%s-be' % self.context.Language()}]
        return called_url(url, headers)        
    
    def secondarykeys_processing(self, jsondata):
        msgid = _(u"not_available")
        not_available = self.context.translate(msgid)
        
        table_ids = ["keyName","key"]
        
        return update_dossiers(jsondata, table_ids, not_available, has_address=False)
        
    def generate_formatted_keys(self, keys):
        results=[]
        for key in keys:
            formatted_key = ''
            for i in range(len(key['key'])):
                if i % 4 == 0 and i != 0:
                    formatted_key += " - "                
                formatted_key += key['key'][i]
            key['formatted_key'] = formatted_key  
            results.append(key)
        return results
                
def make_table_rows(absolute_url, dossiers):
    table = ''
    for dossier in dossiers:
        table+='''
<tr class="secondary_key">
    <td>%s</td>
    <td>%s</td>
    <td><a href="%s/revoke_mandat?key=%s" class="revoke_mandat">revoke</a></td>
</tr>''' % (dossier['keyName'], dossier['formatted_key'], absolute_url, urllib.quote_plus(dossier['key']))       
    return table
