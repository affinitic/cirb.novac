# -*- coding: UTF-8 -*-
from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility
from plone.registry.interfaces import IRegistry

class Happy(BrowserView):
    """
    happy pag browser view
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request        
    
    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()
    
    def happy(self):
        results={}
        results['sso'] = self.get_sso()
        results['waws'] = self.get_waws()
        results['urbis'] = self.get_urbis()        
        return results
    
    def get_sso(self):
        return "sso"
    
    def get_waws(self):
        return "waws"
    
    def get_urbis(self):
        return "urbis"    
    
    