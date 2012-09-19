""" Related
"""
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IFeedPortletInfo, IRelations
from Products.Five.browser import BrowserView
from eea.mediacentre.interfaces import IMediaType
from eea.rdfrepository.interfaces import IFeed, IFeedDiscover
from eea.rdfrepository.plugins.discover import DiscoverPlugin
from eea.rdfrepository.utils import getFeedItemsWithoutDuplicates
from eea.themecentre.interfaces import IThemeMoreLink
from eea.themecentre.interfaces import IThemeTagging
from eea.translations import _
from Products.EEAContentTypes.browser.interfaces import (
    IDocumentRelated, IAutoRelated
)
from p4a.video.interfaces import IMediaPlayer, IVideo
from eea.mediacentre.interfaces import IVideo as MIVideo
from zope.schema.interfaces import IVocabularyFactory
from zope.component import (
    queryAdapter, getUtility,
    getMultiAdapter, queryMultiAdapter
)
from zope.interface import implements


TOP_VIDEOS = 3
MEDIA_ORDER = ['video']

def getObjectInfo(item, request):
    """ Object info
    """
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
             'is_video': MIVideo.providedBy(item),
             'item_type': item.portal_type,
             'item_mimetype':mimetype,
             'item_type_class': item_type_class,
             'item_wf_state': item_wf_state,
             'item_wf_state_class': item_wf_state_class }

    return info

def getBrainInfo(brain, plone_utils):
    """ Brain info
    """
    info = { 'title': brain.Title,
             'brain':brain,
             'uid': brain.UID,
             'description': brain.Description,
             'absolute_url': brain.getURL(),
             'is_video':
             "eea.mediacentre.interface.IVideo" in brain.object_provides,
             'item_type': brain.portal_type,
             'item_type_class': plone_utils.normalizeString(brain.portal_type),
             'item_wf_state': brain.review_state,
             'item_wf_state_class':
             'state-' + plone_utils.normalizeString(brain.review_state)

             #these infos are missing when compared to full info
             #'url': brain.getURL() + "/view",
             #'item_mimetype':mimetype,
             #'has_img': imgview != None and imgview.display() == True,

             }

    return info


def annotateBrainInfo(info, request):
    """Adds details about the object taken from its brain

    Note on the optimization that this achieves:
    There are a couple of cases where there are a lot of results
    (for example from a catalog search of "same theme") that are
    trimmed down to a couple of objects. We don't want to compute
    getObjectInfo for each, because that's expensive.
    Instead we first call getBrainInfo for each brain, trim the
    result and then call annotateBrainInfo for each brain.
    """

    if not info.get('brain'):
        return

    brain = info['brain']
    obj = brain.getObject()
    state = getMultiAdapter((obj, request), name="plone_context_state")
    url = state.view_url()
    imgview = queryMultiAdapter((obj, request), name="imgview")
    info['has_img'] = (imgview != None and imgview.display() == True)
    info['item_mimetype'] = obj.get_content_type()
    info['url'] = url


def annotateByThemeInfo(byTheme, request):
    """Add extra information that can only be retrieved from the full object
    """

    for _theme, infos in byTheme.items():
        for info in infos:
            annotateBrainInfo(info, request)


def annotateThemeInfos(themeinfos, request):
    """ Brain info
    """
    for info in themeinfos:
        annotateBrainInfo(info, request)


def filterDuplicates(items):
    """ filter duplicates
    """
    uids = {}
    for i in items:
        uids[i['uid']] = i
    return uids.values()

    #uids = []
    #ret = []
    #for i in items:
        #if i['uid'] not in uids:
            #uids.append(i['uid'])
            #ret.append(i)
    #return ret


def others(context, brains):
    """Returns a list of brains which do no point to the context
    """
    plone_utils = getToolByName(context, 'plone_utils')
    cid = context.getId()
    return [getBrainInfo(b, plone_utils) for b in brains if (b.getId != cid)]


class AutoRelated(object):
    """ Auto related
    """
    implements(IAutoRelated)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def sameTypeByTheme(self):
        """NOTE: returns full info. The results are limited in number so
        we can afford this
        """
        result = self.sameTheme(portal_type=self.context.portal_type)

        byTheme = {}

        for res in result:
            theme = res['commonThemesIds'][0]
            themeObjs = byTheme.get(theme, [])
            if len(themeObjs) < 3:
                themeObjs.append(res)
                byTheme[theme] = themeObjs

        annotateByThemeInfo(byTheme, self.request)

        # now we have the themes in a dictionary, put them in a list instead
        themes = []
        vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        themeVocab = vocabFactory(self)
        contextThemes = self._contextThemes()

        for themename in contextThemes:
            theme = byTheme.get(themename, None)
            if theme:
                url = IThemeMoreLink(self.context).url(themename)
                themes.append({'name': _(
                    str(themeVocab.getTerm(themename).title)),
                               'items': theme,
                               'more_link': url })
        return themes

    def sameTheme(self, portal_type=None):
        """
        NOTE: returns incomplete info, from getBrainInfo. You need to call
        annotateBrainInfo() if you need full info

        TODO: this should be made a private methods, not callable through
        the normal API, to emphasize that it doesn't return full info.

        """
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).byTheme(portal_type,
                                                  getBrains=True,
                                                  considerDeprecated=True,
                                                  constraints=constraints)

        contextThemes = self._contextThemes()
        #vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        #themeVocab = vocabFactory(self)
        related = []
        plone_utils = getToolByName(self.context, 'plone_utils')

        for item in result:
            # skip articles from auto related by theme since they are related
            # by publication group
            if item.portal_type in ['Article']:
                continue

            if item.getId != self.context.getId():
                commonThemesIds = [ theme for theme in item.getThemes
                                    if theme in contextThemes ]
                #info = getObjectInfo(item.getObject(), self.request)
                info = getBrainInfo(item, plone_utils)
                info['commonThemesIds'] = commonThemesIds
                related.append(info)

        return related

    def autoContext(self, portal_type=None, fill_limit=0):
        """NOTE: returns full info. May end up being slow
        """
        refs = IRelations(self.context).autoContextReferences(portal_type)
        refs = [getObjectInfo(i, self.request) for i in refs]
        theme = self.sameTheme(portal_type)
        items = refs + theme
        if len(items) < fill_limit:
            items += self.sameType(portal_type)
        nondups = filterDuplicates(items)
        annotateThemeInfos(nondups, self.request)
        return nondups

    def sameType(self, portal_type=None):
        """
        NOTE: returns incomplete info, from getBrainInfo. You need to call
        annotateBrainInfo() if you need full info

        TODO: this should be made a private methods, not callable through
        the normal API, to emphasize that it doesn't return full info.

        """
        if portal_type == None:
            portal_type = self.context.portal_type
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).getItems(portal_type,
                                                  getBrains=True,
                                                  considerDeprecated=True,
                                                  constraints=constraints)
        related = others(self.context, result)

        #for item in related:
            ##obj = item.getObject()
            #if item.getId != cid:
                ##info = getObjectInfo(obj, self.request)
                #info = getBrainInfo(item, self.request)
                #related.append(info)

        return related

    def sameTypeByPublicationGroup(self):
        """ for now we don't group by publication group,
            we only return all of same
            type that can have a publication group.
        """
        constraints = {'review_state': 'published'}
        result = IRelations(self.context).byPublicationGroup(
            samePortalType=True,
            getBrains=True,
            constraints=constraints)

        related = others(self.context, result)
        annotateThemeInfos(related, self.request)
        #Note: enable if you notice errors about missing keys

        #for item in result:
            #obj = item.getObject()
            #if item.getId != self.context.getId():
                #info = getObjectInfo(obj, self.request)
                #related.append(info)

        return related

    def _contextThemes(self):
        """ Themes
        """
        theme = queryAdapter(self.context, IThemeTagging)
        if theme is None:
            contextThemes = []
        else:
            contextThemes = theme.nondeprecated_tags
        return contextThemes


class DocumentRelated(BrowserView):
    """ Some docstinrg. """

    implements(IDocumentRelated)

    def __init__(self, context, request):
        super(DocumentRelated, self).__init__(context, request)

        #self.context = utils.context(self)
        self.plone_utils = getToolByName(context, 'plone_utils')
        self.normalize = self.plone_utils.normalizeString

        self.portal_props = getToolByName(context, 'portal_properties')
        self.wf_tool = getToolByName(context, 'portal_workflow')
        self.site_props = self.portal_props.site_properties
        self.use_view = getattr(self.site_props,
                                'typesUseViewActionInListings', [])

        self.related = IRelations(self.context).references()

        self.related_feeds = []
        self.related_pages = []
        self.related_media_with_player = []
        self.related_other = []
        self.related_images = []
        for item in self.related:
            if queryAdapter(item, IVideo):
                self.related_media_with_player.append(item)
            elif item.portal_type == 'Image':
                self.related_images.append(item)
            elif item.portal_type in ['Document', 'Highlight', 'PressRelease',
                                      'Speech', 'AssessmentPart']:
                self.related_pages.append(item)
            else:
                self.related_other.append(item)

    def _all_media(self):
        """ All media
        """
        return self.related_media_with_player + self.related_images

    def bottom_media(self):
        """ Bottom media
        """
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
            links.sort(cmp=lambda x, y: cmp(x['date'], y['date']))

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
        """ Feeds
        """
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
                    feeds = discover.getFeeds(search={ 'theme' : theme,
                                                        'id' : feed.getId() })
                    if len(feeds) > 0:
                        feed = feeds[0]
                    else:
                        continue

            info = IFeedPortletInfo(IFeed(feed))
            for item in info.items:
                entries.append(item)

        entries.sort(cmp=lambda x, y:-cmp(x.published_unparsed,
                                          y.published_unparsed))
        entries = getFeedItemsWithoutDuplicates(entries, sort=True,
                                                published_attr=True)
        return entries

    def mediacount(self):
        """ Count
        """
        return len(self._all_media())

    def multimedia(self):
        """ Mutimedia
        """
        # TODO: delete? Where's this used?
        #multimedia = []
        for item in self.related_media_with_player:
            mimetype = item.get_content_type()
            player_html = queryAdapter(item, name=mimetype,
                                       interface=IMediaPlayer)
            player_html.max_width = 200 - 16
            player_html.autoplay = False
            player_html.autobuffer = False
            return player_html(None, None)
        return None

    def pages(self):
        """ Pages
        """
        pages = []
        for item in self.related_pages:
            pages.append({ 'title': item.Title(),
                           'url': item.absolute_url() })
        return pages

    def other(self):
        """ Other
        """
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
                           'is_video': MIVideo.providedBy(item),
                           'has_img': (imgview != None and
                                       imgview.display() == True )
                           })
        return other

    def top_count(self):
        """ Top count
        """
        return len(self.top_media())

    def top_media(self):
        """ Top media
        """
        media = []

        for item in self.related_media_with_player[:TOP_VIDEOS]:
            info = getObjectInfo(item, self.request)
            media.append(info)
        return media
