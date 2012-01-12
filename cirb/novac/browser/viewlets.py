# -*- coding: UTF-8 -*-
from plone.app.layout.viewlets.common import PathBarViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile, BoundPageTemplate
from cirb.novac.browser.novacview import NovacView


class BreatcrumbViewlet(PathBarViewlet):

    def baseView(self):
        # view attribute of this viewlet is wrong, it should be a
        # real browser view but it is bound to the viewlet that contains this viewlet
        # (PortalHeader being a viewlet itself).
        return self.view.__parent__

    def render(self):
        if isinstance(self.baseView(), NovacView):
            return BoundPageTemplate(ViewPageTemplateFile('templates/breatcrumb.pt'), self)()
        else:
            return self.index()
