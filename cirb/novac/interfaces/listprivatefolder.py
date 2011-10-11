from zope.interface import Interface
# -*- Additional Imports Here -*-
from zope import schema

from cirb.novac import novacMessageFactory as _



class IListPrivateFolder(Interface):
    """Private view for a list of folder"""

    # -*- schema definition goes here -*-
    ws_url = schema.TextLine(
        title=_(u"Ws URL"),
        required=True,
        description=_(u"Put the webservice url"),
    )
#
