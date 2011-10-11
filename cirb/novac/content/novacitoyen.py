"""Definition of the Nova Citoyen content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-

from cirb.novac.interfaces import INovaCitoyen
from cirb.novac.config import PROJECTNAME

NovaCitoyenSchema = folder.ATFolderSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

))

# Set storage on fields copied from ATFolderSchema, making sure
# they work well with the python bridge properties.

NovaCitoyenSchema['title'].storage = atapi.AnnotationStorage()
NovaCitoyenSchema['description'].storage = atapi.AnnotationStorage()

schemata.finalizeATCTSchema(
    NovaCitoyenSchema,
    folderish=True,
    moveDiscussion=False
)


class NovaCitoyen(folder.ATFolder):
    """A plone plugin for Nova Citoyen"""
    implements(INovaCitoyen)

    meta_type = "NovaCitoyen"
    schema = NovaCitoyenSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    # -*- Your ATSchema to Python Property Bridges Here ... -*-

atapi.registerType(NovaCitoyen, PROJECTNAME)
