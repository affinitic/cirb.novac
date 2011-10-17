from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError

from cirb.novac import novacMessageFactory as _

from cirb.novac.browser.novacview import INovacView, NovacView

class IPublicView(Interface):
    """
    Cas view interface
    """

    def test():
        """ test method"""


class PublicView(BrowserView):
    """
    Cas browser view
    """
    implements(IPublicView)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def view_name(self):
        return "public"
        
    def public(self):
        registry = getUtility(IRegistry)
        novac_url = registry['cirb.novac.novac_url']
        json_file = registry['cirb.novac.json_file']
        folder_id = self.request.form.get('id')
        error=False
        msg_error=''
        if not novac_url:
            error=True
            msg_error=_(u'No url for novac url')
        if not folder_id:
            error=True
            msg_error=_(u'No url for novac url')
        
        return {'novac_url':novac_url,'folder_id':folder_id,'error':error,'msg_error':msg_error}
        
    
    def python_json(self):
        oldtimeout = socket.getdefaulttimeout()
        data = ''
        error=False
        url = 'http://ws.irisnetlab.be/nova/pub/dossiers/'+self.request.form.get('id')
        try:
            socket.setdefaulttimeout(7) # let's wait 7 sec            
            request = urllib2.Request(url,headers={'content-type': 'application/json'})            
            #request.add_header('User-Agent', 'Cas/1 +http://www.cirb.irisnet.be/')
            opener = urllib2.build_opener()
            data = opener.open(request).read()
        except HTTPError, e:
            data = _('The server couldn\'t fulfill the request.<br />Error code: %s' % e.code)
            error=True
        except URLError, e:
            data = _('We failed to reach a server.<br /> Reason: %s'% e.reason)
            error=True
        finally:
            socket.setdefaulttimeout(oldtimeout)
        return {'data':data, 'error':error}