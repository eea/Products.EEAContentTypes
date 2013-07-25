""" Interfaces
"""
from zope.interface import Interface, Attribute
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.folder import IATFolder
from eea.mediacentre.interfaces import IVideo

class ICFTRequestor(Interface):
    """ CFT Requestor
    """

class ICallForTender(Interface):
    """ Call for tenders
    """

class IQuickEvent(Interface):
    """ Quick event
    """

class IGeoPositionDecider(Interface):
    """ Geo position decider
    """

    def matchLocation(obj):
        """ Match location """

    def provideInterfaces(obj):
        """ Provide interfaces """

    def run(obj):
        """ Run """

class IGeoPositioned(Interface):
    """ Geo positioned """

class IGeoPosition(Interface):
    """ Geographic coordinates. """

    longitude = Attribute("Geographic longitude")

    latitude = Attribute("Geographic latitude")

    country_code = Attribute("Country code")

    def getCoordinates():
        """ Return longitude and latitude. """


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
