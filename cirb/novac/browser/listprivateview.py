# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.browser import novacview
import urllib

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
        user = self.portal_state.member()
        
        dossier_list_url = '%s%s%s' %(self.novac_url,FOLDER_LIST_WS,"Test")
        dossier_list = novacview.called_url(dossier_list_url, 'application/json')
        results=[]
        import json
        jsondata = json.loads(dossier_list)
        for properties in jsondata:
           
            try:
                address = '%s, %s %s %s' % (properties['numberFrom'],
                                        properties['streetName'],
                                        properties['zipcode'],
                                        properties['municipality'],)
            except:
                address = not_avaiable   
                
            type_dossier = self.get_properties(properties,"typeDossier")
            desc = self.get_properties(properties,'object')
            ref = self.get_properties(properties,'refNova')
            folder_filed = self.get_properties(properties,'folderFiled')
            introduce_on = self.get_properties(properties,'startPublicInquiry')
            lang = self.get_properties(properties,'lang')
            status = self.get_properties(properties,'statusPermit')
          
            results.append({'address':address, 'type_dossier':type_dossier, 'ref':ref,
                            'introduce_on':introduce_on})
        
        return {'novac_url':self.novac_url,'error':error,'msg_error':msg_error, 
                'user':user, 'dossier_list':dossier_list, 'dossier_list_url':dossier_list_url,
                'results':results}
     
    def get_properties(self, prop, prop_name):
        msgid = _(u"not_available")
        not_avaiable = self.context.translate(msgid)
        try:
            return prop[prop_name]
        except:
            return not_avaiable
    
    # view to activate a dossier with the key
    def activate_key(self):
        #key = self.request.form.get('key')
        query_string = self.request.environ['QUERY_STRING']
        key = query_string.replace('key=','')
        
        activate_url = '%s%s%s' %(self.novac_url,ACTIVATION,urllib.quote(key))
        #activate_url = activate_url.encode('utf-8')
        results = novacview.call_put_url(activate_url,'application/xml', query_string)
        
        return 'activate_key : %s <br />%s ' % (activate_url, results)