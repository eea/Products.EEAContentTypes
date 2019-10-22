""" Cache
"""
import logging
from plone import api
from plone.api.exc import CannotGetPortalError
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from zope.component import queryMultiAdapter
from zope.event import notify
from eea.reports.interfaces import IReportContainerEnhanced
from eea.cache.event import InvalidateMemCacheEvent
from eea.cache.event import InvalidateVarnishEvent


logger = logging.getLogger('Products.EEAContentTypes.cache')

DATASETS_INTERFACES= [
    'Products.EEAContentTypes.content.interfaces.IInteractiveMap',
    'Products.EEAContentTypes.content.interfaces.IInteractiveData',
    'Products.EEAContentTypes.content.interfaces.IInfographic',
    'eea.dataservice.interfaces.IEEAFigureGraph',
    'eea.dataservice.interfaces.IDataset',
    'eea.dataservice.interfaces.IEEAFigureMap',
    'eea.indicators.content.interfaces.IIndicatorAssessment']

def invalidate_cache(context, request):
    """ Invalidate cache
    """
    queryMultiAdapter((context, request), name='cache.invalidate',
            default=lambda: False)()

def invalidateCache(obj, event):
    """ Generic cache invalidation policy
    """
    portal = None
    state = None

    try:
        portal = api.portal.get()
        state = api.content.get_state(obj)
    except CannotGetPortalError, err:
        # This happens if you are using bin/instance debug, because debug
        # sessions do not have a request and so the getSite() cannot
        # know which Plone portal you want to get (as there can be
        # multiple Plone sites).
        logger.warn(err)
    except WorkflowException as err:
        # Skip special objects
        logger.warn(err)

    if state != 'published':
        return

    # invalidate frontpage cache
    site = getattr(portal, 'SITE', None)
    request = getattr(obj, 'REQUEST', {})
    invalidate_cache(site, request)

    # invalidate parent cache when context is a default view
    state = queryMultiAdapter((obj, request), name='plone_context_state')
    if state and state.is_default_page():
        invalidate_cache(obj.getParentNode(), request)

    # invalidate publications main section
    if IReportContainerEnhanced.providedBy(obj):
        publications = getattr(site, 'publications', None)
        return invalidate_cache(publications, request)

    # invalidate data and maps main section
    interfaces = queryMultiAdapter((obj, request), name='get_interfaces')
    has_any_of = getattr(interfaces, 'has_any_of', lambda i: False)
    if has_any_of(DATASETS_INTERFACES):
        data_and_maps = getattr(site, 'data-and-maps', None)
        return invalidate_cache(data_and_maps, request)

def invalidateNavigationCache(obj, event):
    """ Invalidate Navigation memcache
    """
    portal_factory = getToolByName(obj, 'portal_factory', None)
    if portal_factory and not portal_factory.isTemporary(obj):
        notify(InvalidateMemCacheEvent(raw=True, dependencies=['navigation']))

def invalidateParentsImageScales(obj, event):
    """ Invalidate varnish thumbs for image's parents.
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
