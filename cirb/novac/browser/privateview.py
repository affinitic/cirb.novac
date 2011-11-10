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
        self.test = ''
        
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
        dossier_id = self.request.form.get('id')
        dossier_url = '%s%s%s' % (self.novac_url,PRIVATE_FODLER_WS,dossier_id)
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
        #key = self.request.form.get('key')
        query_string = self.request.environ['QUERY_STRING']
        mandat = query_string.replace('mandat=','')
        
        #activate_url = '%s%s%s' %(self.novac_url,ACTIVATION,urllib.quote(key))
        #activate_url = activate_url.encode('utf-8')
        #results = call_put_url(activate_url,'application/xml', query_string)
        self.test += '''
        <tr id="secondary_keys"><td>%s</td><td>&nbsp;</td><td>&nbsp;</td></tr>
        ''' % mandat
        return self.get_test()
    
    def get_test(self):
        return self.test
    
    def get_table_lines_secondary_keys(self):        
        """dossier_list_url = '%s%s%s' %(self.novac_url,FOLDER_LIST_WS,"Test")
        dossier_list = called_url(dossier_list_url, 'application/json')
        results=[]
        import json
        jsondata = json.loads(dossier_list)
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        table = ''
        for properties in jsondata:           
            result={} 
            try:
                result['address'] = '%s, %s %s %s' % (properties['numberFrom'],
                                        properties['streetName'], properties['zipcode'], properties['municipality'],)
            except:
                result['address'] = not_avaiable                   
            result['type_dossier'] = get_properties(self.context, properties,"typeDossier")
            result['municipality_owner'] = get_properties(self.context, properties,"municipalityOwner")
            result['dossier_id'] = get_properties(self.context, properties,"id")
            result['lang'] = get_properties(self.context, properties,"languageRequest")
            result['manager'] = get_properties(self.context, properties,"manager")
            result['desc'] = get_properties(self.context, properties,'object')
            result['ref'] = get_properties(self.context, properties,'refNova')
            result['folder_filed'] = get_properties(self.context, properties,'pointCC')
            result['public_inquiry'] = get_properties(self.context, properties,'publicInquiry')
            result['specific_reference'] = get_properties(self.context, properties,'specificReference')
          
            results.append(result)
            table+='''
            <tr  id="content_list_folder">
            <td><a href="%s/wawsprivate_view?id=%s">%s</a></td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            </tr>''' % (self.context.absolute_url(), result['dossier_id'], result['address'], result['ref'], result['type_dossier'],'???')
        """
        if self.test=='':
            self.test = '<tr id="secondary_keys"><td></td><td></td><td></td></tr>'
        return self.get_test()