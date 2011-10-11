"""Definition of the Public Folder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from cirb.novac import novacMessageFactory as _

from cirb.novac.interfaces import IPublicFolder
from cirb.novac.config import PROJECTNAME

PublicFolderSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.StringField(
        'ws_url',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"Ws URL"),
            description=_(u"Put the webservice url"),
        ),
        required=True,
        default=_(u"http://ws.irisnet.be/waws/nova/"),
        validators=('isURL'),
    ),


))

# Set storage on fields copied from ATContentTypeSchema, making sure
# they work well with the python bridge properties.

PublicFolderSchema['title'].storage = atapi.AnnotationStorage()
PublicFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PublicFolderSchema, moveDiscussion=False)


class PublicFolder(base.ATCTContent):
    """A public view of a project"""
    implements(IPublicFolder)

    meta_type = "PublicFolder"
    schema = PublicFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    ws_url = atapi.ATFieldProperty('ws_url')


atapi.registerType(PublicFolder, PROJECTNAME)
