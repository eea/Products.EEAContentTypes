""" Cache
"""

# TODO: this module needs heavy modification to adapt to plone.app.caching, for
# plone4 migration
import logging
import md5

from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from zope.event import notify

from eea.cache.event import InvalidateMemCacheEvent
from eea.cache.event import InvalidateVarnishEvent


# import memcache

logger = logging.getLogger('Products.EEAContentTypes.cache')


def cacheKeyPromotions(method, self):
    """ Cache key for Promotion content-type
    """
    request = self.request
    return (self.portal_url, request.get('LANGUAGE', 'en'))


def cacheKeyHighlights(method, self, portaltypes=('Highlight', 'PressRelease'),
                       scale='thumb'):
    """ Cache key for Highlights content-type
    """
    request = self.request
    return (['frontpage-highlights'], method.__name__, self.portal_url,
            portaltypes, request.get('LANGUAGE', 'en'))


def invalidateHighlightsCache(obj, event):
    """ Invalidate Highlights memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateMemCacheEvent(raw=True,
                                    dependencies=['frontpage-highlights']))


def invalidatePromotionsCache(obj, event):
    """ Invalidate Promotion memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        request = getattr(obj, 'REQUEST', {})
        language = request.get('LANGUAGE', 'en')
        portal_url = getToolByName(obj, 'portal_url')()
        source = ("eea.design.browser.frontpage.getPromotions:('%s', '%s')"
                  ) % (portal_url, language)
        key = md5.new(source).hexdigest()
        notify(InvalidateMemCacheEvent(key=key, raw=True))


def invalidateNavigationCache(obj, event):
    """ Invalidate Navigation memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateMemCacheEvent(raw=True, dependencies=['navigation']))


#
# Varnish
#
def invalidateParentsImageScales(obj, event):
    """
    Invalidate varnish thumbs for image's parents.

    Ticket: #92869
    """
    getParentNode = getattr(obj, 'getParentNode', None)
    if not getParentNode:
        return

    request = getattr(obj, 'REQUEST', None)
    if not request:
        return

    parent = getParentNode()
    imgview = queryMultiAdapter((parent, request), name=u'imgview')

    if not imgview:
        return

    try:
        notify(InvalidateVarnishEvent(parent))
    except Exception as err:
        logger.warn("Can't invalidate varnish for %s: %s",
                    parent.absolute_url(), err)
        return
    else:
        invalidateParentsImageScales(parent, event)
