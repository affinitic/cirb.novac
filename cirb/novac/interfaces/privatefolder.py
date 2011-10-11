from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from cirb.novac import novacMessageFactory as _



class IPrivateFolder(Interface):
    """A private view for a project"""

    # -*- schema definition goes here -*-
    ws_url = schema.TextLine(
        title=_(u"Ws URL"),
        required=True,
        description=_(u"Field description"),
    )
#
