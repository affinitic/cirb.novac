# -*- coding: UTF-8 -*-
from plone.app.layout.viewlets.common import PathBarViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BreatcrumbViewlet(PathBarViewlet):
    
    def render(self):
        return self.index()
    
    index = ViewPageTemplateFile('templates/breatcrumb.pt')
