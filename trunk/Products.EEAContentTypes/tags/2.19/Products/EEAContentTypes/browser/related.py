from zope.component import queryAdapter, getUtility, getMultiAdapter, queryMultiAdapter
from zope.interface import implements
from zope.app.schema.vocabulary import IVocabularyFactory

from Products.CMFPlone import utils
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IFeedPortletInfo, IRelations
from p4a.video.interfaces import IMediaPlayer, IVideo
from p4a.video.interfaces import IVideoEnhanced
from interfaces import IDocumentRelated, IAutoRelated
from eea.rdfrepository.interfaces import IFeed, IFeedDiscover
from eea.rdfrepository.utils import getFeedItemsWithoutDuplicates
from eea.themecentre.interfaces import IThemeTagging
from eea.themecentre.interfaces import IThemeMoreLink
from eea.mediacentre.interfaces import IMediaType
from eea.rdfrepository.plugins.discover import DiscoverPlugin
from eea.translations import _


TOP_VIDEOS = 3
MEDIA_ORDER = ['video']

def getObjectInfo(item, request):
    plone_utils = getToolByName(item, 'plone_utils')
    wf_tool = getToolByName(item, 'portal_workflow')
    state = getMultiAdapter((item, request), name="plone_context_state")

    item_type_class = plone_utils.normalizeString(item.portal_type)
    item_wf_state = wf_tool.getInfoFor(item, 'review_state', '')
    item_wf_state_class = 'state-' + plone_utils.normalizeString(item_wf_state)
    url = state.view_url()
    mimetype = item.get_content_type()
    imgview = queryMultiAdapter((item, request), name='imgview')

    info = { 'title': item.Title(),
             'uid': item.UID(),
             'description': item.Description(),
             'url': url,
             'absolute_url': item.absolute_url(),
             'has_img': imgview != None and imgview.display() == True,
             'is_video': IVideoEnhanced.providedBy(item),
             'item_type': item.portal_type,
             'item_mimetype':mimetype,
             'item_type_class': item_type_class,
             'item_wf_state': item_wf_state,
             'item_wf_state_class': item_wf_state_class }

    return info


def filterDuplicates(items):
    uids = []
    ret = []
    for i in items:
        if i['uid'] not in uids:
            uids.append(i['uid'])
            ret.append(i)
    return ret


class AutoRelated(object):
    implements(IAutoRelated)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sameTypeByTheme(self):
        result = self.sameTheme(portal_type=self.context.portal_type)

        byTheme = {}

        for res in result:
            theme = res['commonThemesIds'][0]
            themeObjs = byTheme.get(theme, [])
            if len(themeObjs) < 3:
                themeObjs.append(res)
                byTheme[theme] = themeObjs
            
        # now we have the themes in a dictionary, put them in a list instead
        themes = []
        vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        themeVocab = vocabFactory(self)
        contextThemes = self._contextThemes()

        for themename in contextThemes:
            theme = byTheme.get(themename, None)
            if theme:
                url = IThemeMoreLink(self.context).url(themename)
                themes.append({'name': _(str(themeVocab.getTerm(themename).title)),
                               'items': theme,
                               'more_link': url })
        return themes

    def sameTheme(self, portal_type=None):
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).byTheme(portal_type,
                                                  getBrains=True,
                                                  considerDeprecated=True,
                                                  constraints=constraints)

        contextThemes = self._contextThemes()
        vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        themeVocab = vocabFactory(self)
        related = []

        for item in result:
            # skip articles from auto related by theme since they are related
            # by publication group
            if item.portal_type in ['Article']:
                continue
            
            obj = item.getObject()
            if item.getId != self.context.getId():
                commonThemesIds = [ theme for theme in item.getThemes
                                    if theme in contextThemes ]
                info = getObjectInfo(obj, self.request)
                info['commonThemesIds'] = commonThemesIds
                related.append(info)

        return related

    def autoContext(self, portal_type=None, fill_limit=0):
        refs = IRelations(self.context).autoContextReferences(portal_type)
        refs = [getObjectInfo(i, self.request) for i in refs]
        theme = self.sameTheme(portal_type) 
        items = refs + theme
        if len(items) < fill_limit:
            items += self.sameType(portal_type)
        return filterDuplicates(items)

    def sameType(self, portal_type=None):
        if portal_type == None:
            portal_type = self.context.portal_type
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).getItems(portal_type,
                                                  getBrains=True,
                                                  considerDeprecated=True,
                                                  constraints=constraints)
        related = []
        for item in result:
            obj = item.getObject()
            if item.getId != self.context.getId():
                info = getObjectInfo(obj, self.request)
                related.append(info)

        return related

    def sameTypeByPublicationGroup(self):
        """ for now we don't group by publication group, we only return all of same
            type that can have a publication group. """
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).byPublicationGroup(samePortalType=True,
                                                  getBrains=True,
                                                  constraints=constraints)

        related = []

        for item in result:
            obj = item.getObject()
            if item.getId != self.context.getId():
                info = getObjectInfo(obj, self.request)
                related.append(info)

        return related
    
    def _contextThemes(self):
        theme = queryAdapter(self.context, IThemeTagging)
        if theme is None:
            contextThemes = []
        else:
            contextThemes = theme.nondeprecated_tags
        return contextThemes

class DocumentRelated(utils.BrowserView):
    """ Some docstinrg. """
    implements(IDocumentRelated)

    def __init__(self, context, request):
        super(DocumentRelated, self).__init__(context, request)
        
        self.context = utils.context(self)
        self.plone_utils = getToolByName(context, 'plone_utils')
        self.normalize = self.plone_utils.normalizeString

        self.portal_props = getToolByName(context, 'portal_properties')
        self.wf_tool = getToolByName(context, 'portal_workflow')
        self.site_props = self.portal_props.site_properties
        self.use_view = getattr(self.site_props, 'typesUseViewActionInListings', [])
        
        self.related = IRelations(self.context).references()

        self.related_feeds = []
        self.related_pages = []
        self.related_media_with_player = []
        self.related_other = []
        self.related_images = []
        for item in self.related:
            if item.portal_type == 'RSSFeedRecipe':
                self.related_feeds.append(item)
            elif queryAdapter(item, IVideo):
                self.related_media_with_player.append(item)
            elif item.portal_type == 'Image':
                self.related_images.append(item)
            elif item.portal_type in ['Document', 'Highlight', 'PressRelease', 'Speech']:
                self.related_pages.append(item)
            else:
                self.related_other.append(item)

    def _all_media(self):
        return self.related_media_with_player + self.related_images

    def bottom_media(self):
        media = {}
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        popup = '/++resource++videoimages/popup_play_icon.png'
        for item in self.related_media_with_player[TOP_VIDEOS:] + \
                self.related_images:
            url = item.absolute_url()
            if item.portal_type in self.use_view:
                url += '/view'
            link = { 'url': url,
                     'text': item.Title(),
                     'date': item.ModificationDate(),
                     'popup_icon': portal.absolute_url() + popup }
            if queryAdapter(item, IVideo):
                link['has_media_player'] = True
            else:
                link['has_media_player'] = False
            if item.portal_type == 'FlashFile':
                link['popup-url'] = item.absolute_url() + \
                        '/flashfile_popup_window'
            else:
                link['popup-url'] = item.absolute_url() + '/popup-play.html'

            category = IMediaType(item).types[0]
            if not media.has_key(category):
                media[category] = []
            media[category].append(link)

        for category, links in media.items():
            links.sort(cmp=lambda x,y: cmp(x['date'], y['date']))

        categories = media.keys()
        media_list = []
        for category in MEDIA_ORDER:
            if category in categories:
                media_list.append({ 'title': category.capitalize() + 's',
                                    'links': media[category] })
        for category in [cat for cat in categories if cat not in MEDIA_ORDER]:
            media_list.append({ 'title': category.capitalize() + 's',
                                'links': media[category] })
        return media_list

    def feeds(self):
        entries = []
        
        theme = queryAdapter(self.context, IThemeTagging)
        if theme and len(theme.tags) > 0:
            # we will only discover on first/one theme
            # TODO: fix discovery to handle more themes at once
            theme = theme.tags[0]
            discover = DiscoverPlugin()
        else:
            theme = None

        for feed in self.related_feeds:
            if theme is not None:
                discover_tags = IFeedDiscover(feed).search_attrs
                if len(discover_tags) > 0:
                    feeds = discover.getFeeds(search= { 'theme' : theme,
                                                        'id' : feed.getId() })
                    if len(feeds) > 0:
                        feed = feeds[0]
                    else:
                        continue

            info = IFeedPortletInfo(IFeed(feed))
            for item in info.items:
                entries.append(item)

        entries.sort(cmp=lambda x,y: -cmp(x.published_unparsed,
                                          y.published_unparsed))
        entries = getFeedItemsWithoutDuplicates(entries, sort=True,
                                                published_attr=True)
        return entries

    def mediacount(self):
        return len(self._all_media())

    def multimedia(self):
        # TODO: delete? Where's this used?
        multimedia = []
        for item in self.related_media_with_player:
            mimetype = item.get_content_type()
            player_html = queryAdapter(item, name=mimetype, interface=IMediaPlayer)
            player_html.max_width = 200-16
            player_html.autoplay = False
            player_html.autobuffer = False
            return player_html(None, None)
        return None

    def pages(self):
        pages = []
        for item in self.related_pages:
            pages.append({ 'title': item.Title(),
                           'url': item.absolute_url() })
        return pages

    def other(self):
        other = []
        
        for item in self.related_other:
            item_type_class = self.normalize(item.portal_type)
            item_wf_state = self.wf_tool.getInfoFor(item, 'review_state', '')
            item_wf_state_class = 'state-' + self.normalize(item_wf_state)
            
            urlview = getMultiAdapter((item, self.request), name="url")
            imgview = queryMultiAdapter((item, self.request), name="imgview")
            url = urlview.listing_url()

            other.append({ 'title': item.Title(),
                           'description': item.Description(),
                           'url': url,
                           'absolute_url': item.absolute_url(),
                           'item_type': item.portal_type,
                           'item_type_class': item_type_class,
                           'item_wf_state': item_wf_state,
                           'item_wf_state_class': item_wf_state_class,
                           'is_video': IVideoEnhanced.providedBy(item),
                           'has_img': imgview != None and imgview.display() == True })
        return other

    def top_count(self):
        return len(self.top_media())

    def top_media(self):
        media = []
       
        for item in self.related_media_with_player[:TOP_VIDEOS]:
            info = getObjectInfo(item, self.request)
            media.append(info)
        return media
