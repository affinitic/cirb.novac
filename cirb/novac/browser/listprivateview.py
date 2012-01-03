# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter


from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from cirb.novac import novacMessageFactory as _
from cirb.novac.utils import *
from cirb.novac.browser.novacview import INovacView, NovacView

import urllib, logging, json

from zope.annotation.interfaces import IAnnotations

FOLDER_LIST_WS = '/nova/sso/dossiers?errn=' # ?errn=errn3 used to test
ACTIVATION = '/waws/sso/activate?key=' # ?errn=errn3 used to test

class IListprivateView(INovacView):
    """
    Cas view interface
    """


class ListprivateView(NovacView):
    """
    Cas browser view
    """
    implements(IListprivateView)

    def __init__(self, context, request):
        super(ListprivateView, self).__init__(context, request)
        self.logger = logging.getLogger('cirb.novac.browser.listprivateview')

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def view_name(self):
        return _(u"Listprivate")
    
    def listprivate_error(self, msg_error):
            self.logger.error(msg_error)
            return {"error":True, "msg_error":msg_error}

    def listprivate(self):
        self.portal_state = getMultiAdapter((self.context, self.request),
                                            name=u'plone_portal_state')
        user = get_user(self.request, self.context)
        if not user:
            msg_error = _('User undefined.')
            return self.listprivate_error(msg_error)
        results = {}
        results['user'] = user['name']
        results['error'] = False
        results['novac_url'] = self.novac_url
        
        return results        
     
    # view to activate a dossier with the key
    def activate_key(self):
        # TODO return 'Bad Key' if 500 is returned by ws
        key = urllib.quote_plus(self.request.form.get('key'))
        #query_string = self.request.environ['QUERY_STRING']
        #key = urllib.quote_plus(query_string.replace('key=',''))        
        user = get_user(self.request, self.context)
        if not user:
            self.logger.error('User is not logged')
        self.logger.info("key : %s - user : %s" % (key, user['id']))
        activate_url = '%s%s%s&RNHEAD=%s' %(self.novac_url,ACTIVATION,key, user['id'])
        #activate_url = activate_url.encode('utf-8')
        headers = [{'Content-Type':'application/xml'}, {'RNHEAD':user['id']}, {'Accept-Language':'%s-be' % self.context.Language()}]
        results = call_put_url(activate_url, headers, 'key=%s&RNHEAD=%s' % (key, user['id']))
        if not results:
            msg_error = _(u"Not able to activate a dossier.")
            return self.listprivate_error(msg_error)
        return {"error":True,}
    
    def get_table_lines_folder(self):
        #errn = urllib.quote(self.request.form.get('errn'))
        dossier_list_url = '%s%s' %(self.novac_url,FOLDER_LIST_WS)
        user = get_user(self.request)
        headers = [{'Content-Type':'application/json'}, {'ACCEPT':'application/json'}, {'RNHEAD':user['id']}, {'Accept-Language':'%s-be' % self.context.Language()}]
        dossier_list = called_url(dossier_list_url, headers, params="")
        #print dossier_list
        empty_table = '<tr id="content_list_folder" style="height: 0px;"><td></td><td></td><td></td><td></td></tr>'
        if not dossier_list:
            return empty_table
        
        jsondata = json_processing(dossier_list)
        if not jsondata:
            return empty_table
        
        results = self.dossier_processing(jsondata)
        
        return make_table_rows(self.context.absolute_url(), results)
    
    def dossier_processing(self, jsondata):
        msgid = _(u"not_available")
        not_available = self.context.translate(msgid)
        print jsondata
        table_ids = ["id","refNova","typeDossier","object","streetName",
                         "numberFrom", "numberTo","zipCode", "municipality",
                         "publicInquiry","startPublicInquiry","endPublicInquiry",
                         "statusPermit","codeDossier", "pointCC","dateCC",
                         "languageRequest","dateDossierComplet","specificReference", 
                         "municipalityOwner", "manager", "dateActivationSSK"]
        
        return update_dossiers(jsondata, table_ids, not_available, has_address=True)

def make_table_rows(absolute_url, dossiers):
    table = ''
    for dossier in dossiers:
        table += '''
<tr  class="content_list_folder">
    <td><a href="%s/private?id=%s">%s</a></td>
    <td>%s</td>
    <td>%s</td>
    <td>%s</td>
</tr>''' % (absolute_url, dossier['id'], dossier['address'], dossier['refNova'],
            dossier['typeDossier'], dossier['dateActivationSSK'])
    return table
        