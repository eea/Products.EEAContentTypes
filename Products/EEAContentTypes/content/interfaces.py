from zope.interface import Interface, Attribute
from p4a.video.interfaces import IVideoEnhanced
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.folder import IATFolder

class ICFTRequestor(Interface):
    pass

class ICallForTender(Interface):
    pass

class IQuickEvent(Interface):
    pass

class IGeoPositionDecider(Interface):
    """ """
    
    def matchLocation(obj):
	""" """
	
    def provideInterfaces(obj):
	""" """
	
    def run(obj):
	""" """

class IGeoPositioned(Interface):
    """ """

class IGeoPosition(Interface):
    """ Geographic coordinates. """
    
    longitude = Attribute("Geographic longitude")
    
    latitude = Attribute("Geographic latitude")
    
    country_code = Attribute("Country code")
    
    def getCoordinates():
	""" Return longitude and latitude. """
 

class IFlashAnimation(IVideoEnhanced):
    width = Attribute("width of flash file")
    height = Attribute("height of flash file")
    bgcolor = Attribute("background color of flash file")


class IArticle(IATNewsItem, IATFolder):
    pass


class IExternalHighlight(IATNewsItem, IATFolder):
    pass


class IExternalPromotion(IATNewsItem):
    pass

class IInteractiveMap(Interface):
    """ Marker interface for all interactive maps content """

class IInteractiveData(Interface):
    """ Marker interface for all interactive data viewers (ex pivot tables) """

