# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.utils import *

PRIVATE_FODLER_WS = '/nova/sso/dossiers/' # ?errn=errn3 used to test
HISTORY =  '/history' # ?errn=errn3 used to test
SECONDARY_KEYS = '/waws/sso/ssks?targetID='
ADD_SECONDARY_KEY = '/waws/sso/ssks?targetID='
ADD_SECONDARY_KEY_NAME = '&keyName='
REVOKE_SECONDARY_KEY = '/waws/sso/ssks/revoke?key='

class IPrivateView(Interface):
    """
    Cas view interface
    """



class PrivateView(BrowserView):
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
        jsondata = called_url(dossier_url, 'application/json')
        
        history_url = '%s%s' % (dossier_url,HISTORY)
        history = called_url(history_url, 'application/json')
        
        
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
        
        
        results['type_dossier'] = get_properties(self.context, properties,"typeDossier")
        results['municipality_owner'] = get_properties(self.context, properties,"municipalityOwner")
        results['dossier_id'] = get_properties(self.context, properties,"id")
        results['lang'] = get_properties(self.context, properties,"languageRequest")
        results['manager'] = get_properties(self.context, properties,"manager")
        results['desc'] = get_properties(self.context, properties,'object')
        results['ref'] = get_properties(self.context, properties,'refNova')
        results['point_cc'] = get_properties(self.context, properties,'pointCC')
        results['public_inquiry'] = get_properties(self.context, properties,'publicInquiry')
        results['specific_reference'] = get_properties(self.context, properties,'specificReference')
        results['x'] = get_properties(self.context, properties,'x')
        results['y'] = get_properties(self.context, properties,'y')
     
        
        owner_folder = True
        
        return {'novac_url':self.novac_url, 'urbis_url':self.urbis_url, 'error':error,'msg_error':msg_error,
                'jsondata':jsondata, 'history':history, 'results':results,
                'owner_folder':owner_folder,}
    
    def activate_mandat(self):
        mandat = urllib.quote(self.request.form.get('mandat'))
        targetID = urllib.quote(self.request.form.get('targetID'))
        query_string = self.request.environ['QUERY_STRING']
        activate_mandat = '%s%s%s%s%s' %(self.novac_url,ADD_SECONDARY_KEY,targetID,
                                     ADD_SECONDARY_KEY_NAME,mandat)
        
        results = call_put_url(activate_mandat,'application/xml', query_string)
        
        return results

    def revoke_mandat(self):
        #key = self.request.form.get('key')
        query_string = self.request.environ['QUERY_STRING']
        key = urllib.quote(self.request.form.get('key'))
        revoke_mandat = '%s%s%s' %(self.novac_url,REFOKE_SECONDARY_KEY,key)        
        results = call_put_url(revoke_mandat,'application/xml', query_string)
        
        return results
    
    def get_table_lines_secondary_keys(self):
        if self.id_dossier:
            targetID = self.id_dossier
        else:
            targetID = urllib.quote(self.request.form.get('targetID'))
                
        secondary_keys_url = '%s%s%s' %(self.novac_url,SECONDARY_KEYS,targetID)
        secondary_keys = called_url(secondary_keys_url, 'application/json')
        if not secondary_keys:
            return '<tr id="secondary_keys" style="height: 0px;"><td></td><td></td><td></td></tr>'
        print secondary_keys
        results=[]
        import json
        jsondata = json.loads(secondary_keys)
        table = ''
        for properties in jsondata:
            result={}
            result['mandat'] = get_properties(self.context, properties,"mandat")
            result['key'] = get_properties(self.context, properties,"key")
          
            results.append(result)
            table+='''
            <tr id="secondary_keys">
            <td>%s</td>
            <td>%s</td>
            <td><a href="%s/revoke_mandat?targetID=%s">revoke</a></td>
            </tr>''' % (result['mandat'], result['key'], 
                        self.context.absolute_url())
       
        return table