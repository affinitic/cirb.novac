"""Definition of the Private Folder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from cirb.novac import novacMessageFactory as _

from cirb.novac.interfaces import IPrivateFolder
from cirb.novac.config import PROJECTNAME

PrivateFolderSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

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

PrivateFolderSchema['title'].storage = atapi.AnnotationStorage()
PrivateFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(PrivateFolderSchema, moveDiscussion=False)


class PrivateFolder(base.ATCTContent):
    """A private view for a project"""
    implements(IPrivateFolder)

    meta_type = "PrivateFolder"
    schema = PrivateFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    ws_url = atapi.ATFieldProperty('ws_url')


atapi.registerType(PrivateFolder, PROJECTNAME)
