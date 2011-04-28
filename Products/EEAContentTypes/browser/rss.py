import zope.interface
import zope.component

from copy import deepcopy
from DateTime import DateTime

from Products.Five import BrowserView
from Products.PloneRSSPortlet import feedparser
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName

from Products.PloneRSSPortlet.browser.interfaces import IRSSFeed
from eea.rdfrepository.interfaces import IFeed
from Products.EEAContentTypes.interfaces import IFeedPortletInfo

class RSSShare(BrowserView):

    def main(self):
        include = self.request.get('include_channels', None)
        nritems = int(self.request.get('nritems', 10))
        if include is not None:
            try:
                include = include.split(',')
            except:
                include = None
            
        rssFeeds = RSSFeedsContent(self.context, self.request).getFeeds()
        if include is not None and include != []:
            rssFeeds = [ feed for feed in rssFeeds
                              if feed.getId() in include ]
        
        ct = getToolByName(self.context, 'portal_catalog')
        query = { 'portal_type' : ('Highlight', 'PressRelease'),
                  'review_state' : 'published',
                  'sort_on' : 'effective',
                  'sort_order' : 'reverse',
                  'effectiveRange' : DateTime() }
        allItems  = ct.searchResults(query)[:nritems]

        for feed in rssFeeds:
            feedItems = feed.getFeed()[:nritems]
            for item in feedItems:
                nItem = { 'pretty_title_or_id' : item['Title'],
                          'Identifier' : item['getURL'],
                          'modified' : item['Date'],
                          'Publisher' : '',
                          'Creator' : '',
                          'Rights' : '',
                          'Subject' : [],
                          'Type' : 'RSSItem from RSSRecipe',
                          }
                nItem.update(item)
                allItems.append( nItem )

        return allItems

class RSSFeedsContent(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.rssFolder = getattr(context, 'rss')

    def getFeeds(self):
        return self.rssFolder.contentValues('RSSFeedRecipe')

    def getDblFeeds(self):
        size = 2
        feedList = self.getFeeds()
        return [feedList[i:i+size] for i in range(0, len(feedList), size)]
    

class RSSFeeds(BrowserView):

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.rssFolder = getattr(context, 'rss')

    def getFeeds(self):
        return [IFeedPortletInfo(IFeed(obj)) for obj in
                self.rssFolder.contentValues('RSSFeedRecipe')]

    def getDblFeeds(self):
        size = 2
        feedList = self.getFeeds()
        return [feedList[i:i+size] for i in range(0, len(feedList), size)]
    

class RSSPortlet(BrowserView):

    zope.interface.implements(IRSSFeed)
    
    def getFeed(self):
        """ Use coverimage_id to get the real image. """

        feed  = deepcopy(getattr(self.context, 'savedFeed', []))
        if feed == []:
            return []
        result = []
        noWithDescription = self.context.getEntriesWithDescription()
        noWithThumbnail =  self.context.getEntriesWithThumbnail()
        descriptionLength = 200
        for item in feed:
            coverimage_id = item.get('coverimage_id', '') or item.get('eeapub_coverimage_id', '')
            if coverimage_id != '' and noWithThumbnail > 0:
                item['Image'] = 'http://dataconnector.eea.europa.eu/getimg.asp?gid=%s' % coverimage_id

            if noWithDescription <= 0:
                item['Description'] = ''

            if len(item['Description']) > descriptionLength:
                descr = item['Description'][:descriptionLength]
                space = item['Description'][descriptionLength:].find(' ')
                shortDescr = '%s%s' %(descr, item['Description'][descriptionLength:][:space])
                item['Description'] = shortDescr
                
            noWithDescription -= 1;
            noWithThumbnail -= 1;            
            result.append(item)
        return result
