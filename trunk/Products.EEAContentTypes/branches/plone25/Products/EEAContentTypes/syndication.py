from bda.feed.atfeedentries import ATPrimaryFieldEnclosure
from bda.feed.atfeedentries import ArchetypesFeedEntry
from bda.feed.interfaces import ILogo
from zope.interface import implements
from zope.component import adapts, queryMultiAdapter

from Products.Archetypes.interfaces import IBaseObject
from Products.ATContentTypes.content.newsitem import ATNewsItem
from Products.basesyndication.interfaces import IEnclosure
from Products.CMFCore.utils import getToolByName

#from valentine.imagescales.browser.interfaces import IImageView

class FeedLogo(object):
    implements(ILogo)
    adapts(IBaseObject)
   
    def __init__(self, context):
        self.context = context   
   
    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')()
        return "%s/%s" % (portal_url, 'eea-print-logo.gif')

class NewsItemEnclosure(ATPrimaryFieldEnclosure):
    implements(IEnclosure)
    adapts(ATNewsItem)

    @property
    def field(self):
        pfield = self.context.getField('image')
        return pfield

class ATContentFeedEntry(ArchetypesFeedEntry):
    adapts(IBaseObject)

    def getBody(self):
        # rss template uses getBody for description so we get description here
        img = queryMultiAdapter((self.context, self.context.REQUEST), name=u'imgview')
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
        portal_calendar = getToolByName(self.context, 'portal_calendar')
        types = portal_calendar.getCalendarTypes()
        if self.context.portal_type in types:
            return self.context.start()
        else:
            return super(ATContentFeedEntry, self).getEffectiveDate()

    def getTitle(self):
        portal_calendar = getToolByName(self.context, 'portal_calendar')
        types = portal_calendar.getCalendarTypes()
        if self.context.portal_type in types:
            location = self.context.getLocation()
            if len(location) > 0:
                return '%s [%s]' % (self.context.Title(), location)
        return self.context.Title()

    def getWebURL(self):
        url = self.context.absolute_url()
        portal_props = getToolByName(self.context, 'portal_properties')
        site_props = getattr(portal_props, 'site_properties')
        view_action = getattr(site_props, 'typesUseViewActionInListings', ())
        if self.context.portal_type in view_action:
            url += '/view'
        url+='?utm_source=EEASubscriptions&amp;utm_medium=RSSFeeds&amp;utm_campaign=Generic'
        return url

    def getXhtml(self):
        """The (x)html body content of this entry, or None
        """       
        return self.context.getText(contenttype="text/xhtml-safe",
                                    encoding='utf-8')
