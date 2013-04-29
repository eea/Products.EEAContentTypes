""" Cache
"""

# TODO: this module needs heavy modification to adapt to plone.app.caching, for
# plone4 migration
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from eea.cache.event import InvalidateCacheEvent
from zope.component import queryMultiAdapter
from zope.event import notify
import logging
import md5

#import memcache

logger = logging.getLogger('Products.EEAContentTypes.cache')


def cacheKeyPromotions(method, self):
    """ Cache key for Promotion content-type
    """
    request = self.request
    return (self.portal_url, request.get('LANGUAGE', 'en'))


def cacheKeyHighlights(method,
        self, portaltypes=('Highlight', 'PressRelease'), scale='thumb'):
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
        notify(InvalidateCacheEvent(raw=True,
                                    dependencies=['frontpage-highlights']))


def invalidatePromotionsCache(obj, event):
    """ Invalidate Promotion memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        portal_url = getToolByName(obj, 'portal_url')()
        source = ("eea.design.browser.frontpage.getPromotions:('%s', '%s')"
                  ) % (portal_url, obj.REQUEST.get('LANGUAGE','en'))
        key = md5.new(source).hexdigest()
        notify(InvalidateCacheEvent(key=key, raw=True))


def invalidateNavigationCache(obj, event):
    """ Invalidate Navigation memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateCacheEvent(raw=True, dependencies=['navigation']))

#
# Varnish
#
def invalidateParentsImageScales(obj, event):
    """
    Updates modification_date for image's parents.
    This way varnish can invalidate thumbs for image's parents.

    Ticket: #4105
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

    setModificationDate = getattr(parent, 'setModificationDate', None)
    if not setModificationDate:
        return

    try:
        setModificationDate(DateTime())
    except Exception, err:
        logger.exception("Can't setModificationDate for %s.\n %s",
                         parent.absolute_url(1), err)
        return
    else:
        parent.reindexObject(idxs=['modified'])
        invalidateParentsImageScales(parent, event)
