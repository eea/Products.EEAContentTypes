""" Feeds
"""
from Acquisition import Implicit
from DateTime import DateTime
from Products.ATContentTypes.interface import IATFolder, IATTopic
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IFeedItemPortletInfo
from Products.EEAContentTypes.interfaces import IFeedPortletInfo
from Products.basesyndication.interfaces import IFeed as IFeedBase
from Products.basesyndication.interfaces import IFeedEntry
from bda.feed.generic import FeedMixin
from eea.rdfrepository.interfaces import IFeed, IFeedItem
from eea.rdfrepository.interfaces import IRDFPortletDataCollector
from eea.rdfrepository.interfaces import IRDFPortletInfo
from eea.themecentre.utils import localized_time
from plone.app.layout.navigation.interfaces import INavigationRoot
from zope.component import adapts
from zope.component import queryAdapter
from zope.interface import implements, Interface
import itertools


class FeedPortletInfo(object):
    """ Info
    """
    implements(IFeedPortletInfo)
    adapts(IFeed)

    def __init__(self, feed):
        self.feed = feed

    @property
    def feed_id(self):
        """ ID
        """
        return self.feed.id

    @property
    def button_link(self):
        """ Link
        """
        return self.feed.feed_url

    @property
    def title(self):
        """ Title
        """
        return self.feed.title

    @property
    def title_link(self):
        """ Title link
        """
        return self.feed.home_url

    @property
    def more_link(self):
        """ More link
        """
        return self.feed.home_url

    @property
    def items(self):
        """ Items
        """
        noWithDescription = self.feed.get('entries_with_description')
        noWithThumbnail = self.feed.get('entries_with_thumbnail')
        descriptionLength = 200
        result = []

        for item in self.feed.items:
            image = None
            if noWithThumbnail and noWithThumbnail > 0:
                coverimage_id = item.get('coverimage_id') or \
                                item.get('eeapub_coverimage_id')
                image_url = item.get('image_url') or \
                            item.get('eeapub_image_url')
                if coverimage_id and noWithThumbnail > 0:
                    image = (
                        'http://dataconnector.eea.europa.eu/getimg.asp?gid=%s' %
                        coverimage_id)
                elif image_url:
                    image = image_url

            description = None
            if noWithDescription and noWithDescription > 0:
                description = item.get('description')
                if description and len(description) > descriptionLength:
                    descr = description[:descriptionLength]
                    after_descr = description[descriptionLength:]
                    space = after_descr.find(' ')
                    shortDescr = '%s%s' % (descr, after_descr[:space])
                    item.description = shortDescr

            noWithDescription -= 1
            noWithThumbnail -= 1

            feed_item = IFeedItemPortletInfo(item)
            feed_item.image = image
            feed_item.description = description
            feed_item.coverage = item.get('dc_coverage') or None
            result.append(feed_item)

        return result


class FeedItemPortletInfo(object):
    """ Item info
    """
    implements(IFeedItemPortletInfo)
    adapts(IFeedItem)

    def __init__(self, item):
        self.item = item
        self.description = None
        self.image = None

    @property
    def detail(self):
        """ Detail
        """
        return self.published

    @property
    def title(self):
        """ Title
        """
        return self.item.title

    @property
    def published_unparsed(self):
        """ Published
        """
        published = self.item.get('published')
        return published

    @property
    def published(self):
        """ Published
        """
        published = self.published_unparsed
        if published:
            if published[-1] == 'W':
                # feeds shouldn't have dates ending with W,
                # but there are those that do
                published = published[:-1] + 'Z'

            return localized_time(published)
        else:
            return None

    @property
    def url(self):
        """ URL
        """
        return self.item.url

    @property
    def summary(self):
        """ Description
        """
        return self.item.get('summary')


class ContextAwareFeedPortletInfo(FeedPortletInfo):
    """ Portlet info
    """
    implements(IRDFPortletInfo)
    adapts(Interface, IFeed)

    def __init__(self, context, feed):
        self.context = context
        self.feed = feed

    @property
    def title_link(self):
        """ Title link
        """
        return self.more_link

    @property
    def more_link(self):
        """ More link
        """
        # check if the link is already cached
        if not hasattr(self, '_link'):
            catalog = getToolByName(self.context, 'portal_catalog')
            portal_types = getToolByName(self.context, 'portal_types')
            types = portal_types.objectIds()

            res = catalog.searchResults({
                'path' : { 'query':'/'.join(self.context.getPhysicalPath()),
                           'depth': 1},
                'Title' : self.feed.title,
                'portal_type' : types })

            if len(res):
                self._link = res[0].getURL()
            else:
                self._link = (self.context.absolute_url() + '/listfeed?feed=' +
                              self.feed.id)

        return self._link


class NavigationRootRDFPortletDataCollector(object):
    """ Data collector
    """
    implements(IRDFPortletDataCollector)
    adapts(INavigationRoot)

    def __init__(self, context):
        self.context = context

    @property
    def feeds(self):
        """ Feeds
        """
        return []


class FolderFeed(FeedMixin, Implicit):
    """Feed bound to folders"""

    adapts(IATFolder)
    implements(IFeedBase)

    def __init__(self, context):
        self.context = context

    def getMaxEntries(self):
        """ Max entries
        """
        syntool = getToolByName(self.context, 'portal_syndication')
        return syntool.getMaxItems()

    def getFeedEntries(self, max_only=True):
        """A sequence of IFeedEntry objects.
        """
        pc = getToolByName(self.context, "portal_catalog")
        brains = pc.searchResults(path=self.context.absolute_url(relative=True),
                sort_on="effective", sort_order="reverse")
        res = []
        for brain in brains:
            obj = brain.getObject()
            entry = queryAdapter(obj, IFeedEntry)
            if entry is not None:
                res.append(entry)
        return res[:self.getMaxEntries()]

    def getWebURL(self):
        """ Web URL
        """
        return self.context.absolute_url()

    def getTitle(self):
        """ Title
        """
        return self.context.Title()

    def getDescription(self):
        """ Description
        """
        return self.context.Description()

    def getUID(self):
        """ UID
        """
        return self.context.UID()

    def getSortedFeedEntries(self):
        """ Feed entries
        """
        return self.getFeedEntries()

    def getEncoding(self):
        """ Encoding
        """
        return self.encoding

    def getModifiedDate(self):
        """ Modified date
        """
        return DateTime(self.context.modified())

    def getImageURL(self):
        """ Image URL
        """
        return self.imageURL


class TopicFeed(FolderFeed):
    """ Topic
    """
    adapts(IATTopic)
    implements(IFeedBase)

    def getFeedEntries(self, max_only=True):
        """ Entries
        """
        brains = self.context.queryCatalog()

        def slice():
            """ Slice
            """
            for brain in brains:
                obj = brain.getObject()
                entry = queryAdapter(obj, IFeedEntry)
                if entry is not None:
                    yield(entry)

        return list(itertools.islice(slice(), self.getMaxEntries()))

    def getModifiedDate(self):
        """ Modified date
        """
        return DateTime(self.context.modified())
