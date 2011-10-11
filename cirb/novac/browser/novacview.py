from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from cirb.novac import novacMessageFactory as _

import re, os
import urllib2, socket
from urllib2 import URLError, HTTPError

class INovacView(Interface):
    """
    Cas view interface
    """

    def test():
        """ test method"""


class NovacView(BrowserView):
    """
    Cas browser view
    """
    implements(INovacView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def novac(self):
        """
        novac method
        """
        data = {}
        ws_urbis = ''
        ws_waws = ''
        private_url= ''
        for elem in self.context.contentValues():
            if elem.getPortalTypeName() == 'Urbis Map':
                ws_urbis = elem.getWs_urbis()
            if elem.getPortalTypeName() == 'Public Folder':
                ws_waws = elem.getWs_url()
            if elem.getPortalTypeName() == 'List Private Folder':
                private_url = elem.absolute_url()
        
        if not ws_urbis:
            return {'error':True, 'error_text': _('Add a Urbis Map')}
        if not ws_waws:
            return {'error':True, 'error_text': _('Add a Public Folder')}
        if not private_url:
            return {'error':True, 'error_text': _('Add a Lsit Private Folder')}
            
        
        return {'ws_urbis':ws_urbis, 'ws_waws':ws_waws, 'private_url':private_url, 'error':False}
