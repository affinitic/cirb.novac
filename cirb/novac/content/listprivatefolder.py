"""Definition of the List Private Folder content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from cirb.novac import novacMessageFactory as _

from cirb.novac.interfaces import IListPrivateFolder
from cirb.novac.config import PROJECTNAME

ListPrivateFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((

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

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

ListPrivateFolderSchema['title'].storage = atapi.AnnotationStorage()
ListPrivateFolderSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    ListPrivateFolderSchema,
    folderish=True,
    moveDiscussion=False
)


class ListPrivateFolder(folder.ATFolder):
    """Private view for a list of folder"""
    implements(IListPrivateFolder)

    meta_type = "ListPrivateFolder"
    schema = ListPrivateFolderSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-
    ws_url = atapi.ATFieldProperty('ws_url')


atapi.registerType(ListPrivateFolder, PROJECTNAME)
