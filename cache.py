import os
import md5
import cPickle
from zope.interface import directlyProvides
from zope.component import queryUtility
from zope.event import notify
import zope.thread
from plone.memoize.interfaces import ICacheChooser
from plone.memoize.ram import AbstractDict
import memcache
from Products.CMFCore.utils import getToolByName
from lovely.memcached.utility import MemcachedClient
from lovely.memcached.interfaces import IMemcachedClient
from lovely.memcached.event import InvalidateCacheEvent
from eea.promotion.interfaces import IPromoted

DEPENDENCIES = { 'frontpage-highlights' : ['Products.EEAContentTypes.browser.frontpage.getHigh',
                                           'Products.EEAContentTypes.browser.frontpage.getMedium',
                                           'Products.EEAContentTypes.browser.frontpage.getLow'],
                 'navigation' : ['Products.NavigationManager.NavigationManager.getTree',],
                 'eea.facetednavigation': ['eea.facetednavigation.browser.app.query.__call__',
                                           'eea.facetednavigation.browser.app.counter.__call__',],
                 'eea.sitestructurediff': ['eea.sitestructurediff.browser.sitemap.data',],
                 }

class MemcacheAdapter(AbstractDict):
    def __init__(self, client, globalkey=''):
        self.client = client

        dependencies = []
        if globalkey:
            for k, v in DEPENDENCIES.items():
                if globalkey in v:
                    dependencies.append(k)

        self.dependencies = dependencies

    def _make_key(self, source):
        return md5.new(source).hexdigest()

    def __getitem__(self, key):
        cached_value = self.client.query(self._make_key(key), raw=True)
        if cached_value is None:
            raise KeyError(key)
        else:
            return cPickle.loads(cached_value)

    def __setitem__(self, key, value):
        cached_value = cPickle.dumps(value)
        self.client.set( cached_value, self._make_key(key), raw=True, dependencies=self.dependencies)

def frontpageMemcached():
    servers=os.environ.get(
        "MEMCACHE_SERVER", "127.0.0.1:11211").split(",")
    return MemcachedClient(servers, defaultNS=u'frontpage')

def choose_cache(fun_name):
    client = queryUtility(IMemcachedClient)
    return MemcacheAdapter(client, globalkey=fun_name)

directlyProvides(choose_cache, ICacheChooser)


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
      source = "Products.EEAContentTypes.browser.frontpage.getPromotions:('%s', '%s')" % (portal_url, obj.REQUEST.get('LANGUAGE','en'))
      key = md5.new(source).hexdigest()
      notify(InvalidateCacheEvent(key=key, raw=True))

def invalidateNavigationCache(obj, event):
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateCacheEvent(raw=True, dependencies=['navigation']))


