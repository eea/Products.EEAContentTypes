""" Interfaces
"""
from zope.interface import Interface, Attribute

from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.folder import IATFolder
from Products.EEAContentTypes.interfaces import IEEAContent
from eea.mediacentre.interfaces import IVideo


class ICallForTender(Interface):
    """ Call for tenders
    """


class IQuickEvent(Interface):
    """ Quick event
    """


class ICountryRegionSection(Interface):
    """ CountryRegionSection content type
    """


class IFlashAnimation(Interface):
    """ Flash animation
    """
    width = Attribute("width of flash file")
    height = Attribute("height of flash file")
    bgcolor = Attribute("background color of flash file")


class ICloudVideo(IVideo):
    """  Cloud Video marker interface
    """


class IArticle(IATNewsItem, IATFolder):
    """ Article
    """


class IExternalHighlight(IATNewsItem, IATFolder):
    """ External highlight
    """


class IExternalPromotion(IATNewsItem):
    """ External Promotion
    """


class IInteractiveMap(Interface):
    """ Marker interface for all interactive maps content
    """


class IInteractiveData(Interface):
    """ Marker interface for all interactive data viewers (ex pivot tables)
    """


class IGISMapApplication(Interface):
    """ Marker interface for GIS Map Applications
    """


class IInteractiveDashboard(Interface):
    """ Marker interface for Dashboards (Tableau)
    """


class IInfographic(IEEAContent):
    """ Infographic
    """


class IGeoPositioned(Interface):
    """ Dummy interface added due to #18351. We have old pickled object
        versions implementing this, and as such, do not remove this interface
    """
