from plone.app.layout.viewlets.common import PathBarViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class BreatcrumbViewlet(PathBarViewlet):
    index = ViewPageTemplateFile('templates/breatcrumb.pt')
