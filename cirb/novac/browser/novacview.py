from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

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
    
    def view_name(self):
        return "novac"
    
    def novac(self):
        """
        novac method
        """
        registry = getUtility(IRegistry)
        novac_url = registry['cirb.novac.novac_url']
        urbis_url = registry['cirb.urbis.urbis_url']
        json_file = registry['cirb.novac.json_file']
        error=False
        msg_error=''
        if not novac_url:
            error=True
            msg_error=_(u'No url for cirb.novac.novac_url')
        if not urbis_url:
            error=True
            msg_error=_(u'No url for cirb.urbis.urbis_url')
        if not json_file:
            error=True
            msg_error=_(u'No json_file')
        private_url='wawslistprivate_view'
        return {'novac_url':novac_url,'urbis_url':urbis_url,
                'json_file':json_file,
                'private_url':private_url,'error':error,'msg_error':msg_error}
        