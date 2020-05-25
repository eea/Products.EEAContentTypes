""" Interfaces
"""
from zope.interface import Interface
from zope import schema
from Products.EEAContentTypes.config import EEAMessageFactory as _


class IScreenshotPortalType(Interface):
    """ Screenshot settings
    """
    title = schema.TextLine(
        title=_(u'Title'),
        description=_(u'Title'),
        required=True
    )
    emulate = schema.TextLine(
        title=_(u'Emulate'),
        description=_(u'Emulate web device example: iPhone 6'),
        required=False
    )
    waitforselector = schema.TextLine(
        title=_(u'Wait for selector'),
        description=_(u'Wait for the selector to appear in page'),
        required=False
    )
    el = schema.TextLine(
        title=_(u'EL'),
        description=_(u'Css selector document.querySelector'),
        required=False
    )
    click = schema.TextLine(
        title=_(u'Click'),
        description=_(u'Example: ".selector>a" excellent way to close popups " \
                        "or to click some buttons on the page.'),
        required=False
    )
    no = schema.TextLine(
        title=_(u'Exclude'),
        description=_(u'Exclude "image", "stylesheet", "script", "font"'),
        required=False
    )
    pdf = schema.Bool(
        title=_(u'Pdf'),
        description=_(u'Generate pdf'),
        default=False
    )
    fullPage = schema.Bool(
        title=_(u'Full Page'),
        description=_(u'It will take screenshot of entire web page if is true.'),
        default=True
    )
    w = schema.Int(
        title=_(u'Width'),
        description=_(u'Width of the Web Page in px'),
        required=False,
        default=1920
    )
    h = schema.Int(
        title=_(u'Heigth'),
        description=_(u'Height of the Web Page in px'),
        required=False,
        default=1080
    )
    waitfor = schema.Int(
        title=_(u'Wait for'),
        description=_(u'Wait time for the page load in milliseconds'),
        required=False
    )
    portal_type = schema.Choice(
        title=_(u'Portal type'),
        description=_(u'Select the portal type for which these settings apply'),
        vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes",
        required=True
    )
    service_url = schema.URI(
        title=_(u'Service URL'),
        description=_(u'Screenshot service url'),
        required=True,
        default='https://screenshot.eea.europa.eu'
    )


class IScreenshotTool(Interface):
    """ IScreenshotTool """

class IScreenshotCatalog(Interface):
    """ IScreenshotCatalog """
