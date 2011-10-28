# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.browser import novacview

FOLDER_LIST_WS = '/nova/sso/dossiers?errn=errn3' # ?errn=errn3 used to test
ACTIVATION = '/waws/sso/errn3/activate?key=' # ?errn=errn3 used to test

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
        
        dossier_list_url = '%s%s' %(self.novac_url,FOLDER_LIST_WS)
        dossier_list = novacview.call_put_url(dossier_list_url, 'application/xml', 'errn=errn3')
        
        return {'novac_url':self.novac_url,'error':error,'msg_error':msg_error, 
                'user':user, 'dossier_list':dossier_list, 'dossier_list_url':dossier_list_url}
    
    
    # view to activate a dossier with the key
    def activate_key(self):
        #key = self.request.form.get('key')
        query_string = self.request.environ['QUERY_STRING']
        key = query_string.replace('key=','')
        
        activate_url = '%s%s%s' %(self.novac_url,ACTIVATION,key)
        activate_url = activate_url.encode('utf-8')
        results = novacview.call_put_url(activate_url,'application/xml', query_string)
        
        return 'activate_key : %s <br />%s ' % (activate_url, results)