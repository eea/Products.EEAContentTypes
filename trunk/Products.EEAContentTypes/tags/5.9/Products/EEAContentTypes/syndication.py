""" EEA CT syndication
"""
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from bda.feed.atfeedentries import ATPrimaryFieldEnclosure
from bda.feed.atfeedentries import ArchetypesFeedEntry
from bda.feed.interfaces import ILogo
from zope.component import adapts, queryMultiAdapter
from zope.interface import implements
import logging

logger = logging.getLogger("Products.EEAContentTypes")


class FeedLogo(object):
    """ Logo
    """
    implements(ILogo)
    adapts(IBaseObject)

    def __init__(self, context):
        self.context = context

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return "%s/%s" % (portal_url, 'eea-print-logo.gif')


class NewsItemEnclosure(ATPrimaryFieldEnclosure):
    """ News Item enclosure
    """
    adapts(ATNewsItem)

    @property
    def field(self):
        """ Field
        """
        pfield = self.context.getField('image')
        return pfield


class ATContentFeedEntry(ArchetypesFeedEntry):
    """ ATContent Feed Entry
    """
    adapts(IBaseObject)

    def getBody(self):
        """ Body
        """
        # rss template uses getBody for description so we get description here
        img = queryMultiAdapter((self.context, self.context.REQUEST),
                                name=u'imgview')
        if img is not None and img.display('mini'):
            # images, highlights, press releases etc have an 'image'
            # field - if so then we show a resized version of the image
            result = '<p><img src="%s" /></p><p>%s</p>' % \
                     (img('mini').absolute_url(),
                      self.context.Description())
        else:
            result = self.context.Description()
        return result

    def getEffectiveDate(self):
        """ Effective date
        """
        portal_calendar = getToolByName(self.context, 'portal_calendar')
        types = portal_calendar.getCalendarTypes()
        if self.context.portal_type in types:
            return self.context.start()
        else:
            return self.effectiveDate

    def getModifiedDate(self):
        """ Modified date """
        return self.modifiedDate

    def getAuthor(self):
        """ Author """
        return self.author

    def getTags(self):
        """ Tags """
        return self.tags

    def getEnclosure(self):
        """ Enclosure """
        try:
            return self.enclosures and self.enclosures[0] or []
        except Exception, err:
            logger.warning("Got an error while trying to get "
                           "enclosure for object %s: %s", self.context, err)
            #the problem is caused by the fact that some blob images
            #don't have the filename set. we should fix that
            return []

    def getTitle(self):
        """ Title
        """
        portal_calendar = getToolByName(self.context, 'portal_calendar')
        types = portal_calendar.getCalendarTypes()
        if self.context.portal_type in types:
            location = self.context.getLocation()
            if len(location) > 0:
                return '%s [%s]' % (self.context.Title(), location)
        return self.context.Title()

    def getWebURL(self):
        """ URL
        """
        url = self.context.absolute_url()
        portal_props = getToolByName(self.context, 'portal_properties')
        site_props = getattr(portal_props, 'site_properties')
        view_action = getattr(site_props, 'typesUseViewActionInListings', ())
        if self.context.portal_type in view_action:
            url += '/view'
        url += ('?utm_source=EEASubscriptions&amp;utm_medium=RSSFeeds&amp;' +
                'utm_campaign=Generic')
        return url

    def getXhtml(self):
        """The (x)html body content of this entry, or None
        """
        return self.context.getText(contenttype="text/xhtml-safe",
                                    encoding='utf-8')
