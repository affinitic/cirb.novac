from plone.theme.interfaces import IDefaultPloneLayer
from zope.viewlet.interfaces import IViewletManager


class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
       If you need to register a viewlet only for the
       "Urbis Map" theme, this interface must be its layer
       (in urbis/viewlets/configure.zcml).
    """
    
class IAboveContent(IViewletManager):
    """
    """
    
from zope.interface import Interface

class INovacCustomization(Interface):
    """This interface is registered in profiles/default/browserlayer.xml,
    and is referenced in the 'layer' option of various browser resources.
    When the product is installed, this marker interface will be applied
    to every request, allowing layer-specific customisation.
    """