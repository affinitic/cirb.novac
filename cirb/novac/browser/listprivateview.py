# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.utils import *
import urllib, logging, json

from zope.annotation.interfaces import IAnnotations

FOLDER_LIST_WS = '/nova/sso/dossiers?errn=' # ?errn=errn3 used to test
ACTIVATION = '/waws/sso/activate?key=' # ?errn=errn3 used to test

class IListprivateView(Interface):
    """
    Cas view interface
    """



class ListprivateView(BrowserView):
    """
    Cas browser view
    """
    implements(IListprivateView)

    def __init__(self, context, request):
        self.logger = logging.getLogger('cirb.novac.browser.listprivateview')
        self.context = context
        self.request = request        
        registry = getUtility(IRegistry)
        self.novac_url = registry['cirb.novac.novac_url']

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def listprivate(self):
        
        error=False
        msg_error=''
        if not self.novac_url:
            error=True
            msg_error=_(u'No url for novac url')        
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        user = get_user(self.request, self.context)
        
        dossier_list_url = '%s%s%s' %(self.novac_url,FOLDER_LIST_WS,user['id'])   
        dossier_list = called_url(dossier_list_url, [{'Content-Type':'application/json'}, {'ACCEPT':'application/json'}, {'lang':self.context.Language()}], lang=self.context.Language())
        results=[]
        import json
        jsondata=''
        try:
            jsondata = json.loads(dossier_list)
        except:
            error=True
            msg_error=_(u'Not able to decode json file')  
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        
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
        
        return {'novac_url':self.novac_url,'error':error,'msg_error':msg_error, 
                'user':user['name'], 'dossier_list':dossier_list, 'dossier_list_url':dossier_list_url,
                'results':results}
     
    # view to activate a dossier with the key
    def activate_key(self):
        
        # TODO return 'Bad Key' if 500 is returned by ws
        key = urllib.quote_plus(self.request.form.get('key'))        
        #query_string = self.request.environ['QUERY_STRING']
        #key = urllib.quote_plus(query_string.replace('key=',''))        
        user = get_user(self.request)
        self.logger.info("key : %s - user : %s" % (key, user['id']))
        activate_url = '%s%s%s&RNHEAD=%s' %(self.novac_url,ACTIVATION,key, user['id'])
        #activate_url = activate_url.encode('utf-8')
        results = call_put_url(activate_url,[{'Content-Type':'application/xml'},{'RNHEAD':user['id']}], 'key=%s&RNHEAD=%s' % (key,user['id']))
        
        return 'activate_key : %s <br />%s ' % (activate_url, results)
    
    def get_table_lines_folder(self):        
        #errn = urllib.quote(self.request.form.get('errn'))
        dossier_list_url = '%s%s' %(self.novac_url,FOLDER_LIST_WS)
        user = get_user(self.request)
        dossier_list = called_url(dossier_list_url, [{'Content-Type':'application/json'}, {'ACCEPT':'application/json'}, {'RNHEAD':user['id']}, {'lang':self.context.Language()}], lang=self.context.Language(), params="")
        #print dossier_list
        if not dossier_list:
            return '<tr id="content_list_folder" style="height: 0px;"><td></td><td></td><td></td><td></td></tr>'
        results=[]
        
        try:
            jsondata = json.loads(dossier_list)
        except ValueError, e:
            self.logger.error('Json value error : %s.' % e.message)
        except SyntaxError, e:
            self.logger.error('Json bad formatted : %s.' % e.message)
            
        msgid = _(u"not_available")
        not_available = self.context.translate(msgid)
        
        table_ids = ["id","refNova","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","specificReference", 
                         "municipalityOwner", "manager"]
        
        results = update_dossiers(jsondata, table_ids, not_available)        
        return make_table_rows(self.context.absolute_url(), results)


def make_table_rows(absolute_url, dossiers):
    table = ''
    for dossier in dossiers:
        table+='''
<tr  class="content_list_folder">
    <td><a href="%s/wawsprivate_view?id=%s">%s</a></td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>''' % (absolute_url, dossier['id'], dossier['address'], dossier['refNova'],
            dossier['typeDossier'], dossier['dateDossierComplet'])
    return table
        