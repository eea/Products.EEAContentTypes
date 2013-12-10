""" Interfaces
"""
from zope.interface import Interface, Attribute
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.folder import IATFolder
from Products.EEAContentTypes.interfaces import IEEAContent
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


class IInfographic(IEEAContent):
    """ Infographic
    """
