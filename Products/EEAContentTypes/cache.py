
import md5
from zope.event import notify



import memcache
from Products.CMFCore.utils import getToolByName
from lovely.memcached.event import InvalidateCacheEvent


def cacheKeyPromotions(method, self):
    request = self.request
    return (self.portal_url, request.get('LANGUAGE', 'en'))

def cacheKeyHighlights(method, self, portaltypes=('Highlight', 'PressRelease'),scale='thumb'):
    request = self.request
    return (['frontpage-highlights'], method.__name__, self.portal_url, portaltypes, request.get('LANGUAGE', 'en'))

def invalidateHighlightsCache(obj, event):
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
      notify(InvalidateCacheEvent(raw=True, dependencies=['frontpage-highlights']))

def invalidatePromotionsCache(obj, event):
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
      portal_url = getToolByName(obj, 'portal_url')()
      source = "eea.design.browser.frontpage.getPromotions:('%s', '%s')" % (portal_url, obj.REQUEST.get('LANGUAGE','en'))
      key = md5.new(source).hexdigest()
      notify(InvalidateCacheEvent(key=key, raw=True))

def invalidateNavigationCache(obj, event):
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateCacheEvent(raw=True, dependencies=['navigation']))


