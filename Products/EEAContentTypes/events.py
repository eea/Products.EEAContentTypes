""" Event handlers
"""
import requests
import logging
import urllib
from cStringIO import StringIO
from BeautifulSoup import BeautifulSoup as bs
from DateTime import DateTime
from HTMLParser import HTMLParser
from PIL import Image
from Products.CMFPlone.utils import getToolByName
from plone.api.portal import getSite
from plone.app.async.interfaces import IAsyncService
from zope.component.interfaces import IObjectEvent
from zope.component.interfaces import ObjectEvent
from zope.component import queryUtility
from zope.interface import Attribute
from zope.interface import implements

logger = logging.getLogger('Products.EEAContentTypes')


def handle_content_state_changed(obj, event):
    """ Set effective to now if effected is not set and object is published
    """
    _marker = object()
    if event.workflow.getInfoFor(obj, 'review_state', _marker) == 'published':
        effective = event.object.effective_date
        if not effective:
            now = DateTime()
            obj.setEffectiveDate(now)


class IGISMapApplicationWillBeRemovedEvent(IObjectEvent):
    """An interactive map will be removed."""
    oldParent = Attribute("The old location parent for the object.")
    oldName = Attribute("The old location name for the object.")


class GISMapApplicationWillBeRemovedEvent(ObjectEvent):
    """An interactive map will be removed from a container.
    """
    implements(IGISMapApplicationWillBeRemovedEvent)

    def __init__(self, obj, oldParent=None, oldName=None):
        ObjectEvent.__init__(self, obj)
        self.oldParent = oldParent
        self.oldName = oldName


def gis_set_image(obj, evt):
    """Set image using screenshoteer service after object is created"""
    url = obj.arcgis_url
    if not url:
        logger.error(
            "Can't set image for %s, url wasn't provided." % obj.absolute_url())
        return

    img = obj.getImage()
    if img.get_size() != 0:
        logger.error("The gis map application already has an image set, not " \
                     "triggering async job for %s" % obj.absolute_url())
        return

    try:
        async_service = queryUtility(IAsyncService)
        if async_service is None:
            logger.warn(
                "Can't set image using async. plone.app.async NOT installed!")
            return

        obj.scheduled_at = DateTime()
        async_queue = async_service.getQueues()['']
        async_service.queueJobInQueue(
            async_queue, ('default',),
            async_screenshoteer_set_image(obj, url),
            obj,
            scheduled_at=obj.scheduled_at
        )
    except Exception as err:
        logger.error(
                "Error while setting image for %s failed with message: %s",
                obj.absolute_url(),
                err.msg)


def dashboard_set_image(obj, evt):
    """Set image using screenshoteer service after object is created"""
    if obj.embed() in [None, '']:
        logger.error("The dashboard doesn't have embedded code, can't " \
                     "set image %s" % obj.absolute_url())
        return

    img = obj.getImage()
    if img.get_size() != 0:
        logger.error("The dashboard already has an image set, not triggering " \
                     "async job for %s" % obj.absolute_url())
        return

    parsed = HTMLParser().unescape(obj.embed())
    parsed = urllib.unquote(parsed)
    embed_html = bs(parsed)

    url = ''
    params = {}
    for param in embed_html.findAll('param'):
        params.update({param['name']: param['value']})

    url = params['host_url'] + params['site_root'] + '/views/' + \
          params['name'] + '?:embed=y' + '&:showVizHome=no' + '&:loadOrderID=0'
    del params['site_root']
    del params['name']
    for name, value in params.items():
        url += '&:' + name + '=' + value

    try:
        async_service = queryUtility(IAsyncService)
        if async_service is None:
            logger.warn(
                "Can't set image using async. plone.app.async NOT installed!")
            return

        obj.scheduled_at = DateTime()
        async_queue = async_service.getQueues()['']
        async_service.queueJobInQueue(
            async_queue, ('default',),
            async_screenshoteer_set_image(obj, url),
            obj,
            scheduled_at=obj.scheduled_at
        )
    except Exception as err:
        logger.error(
                "Error while setting image for %s failed with message: %s",
                obj.absolute_url(),
                err.msg)


def async_screenshoteer_set_image(obj, url):
    """ extract url from embed field for Dashboards, request to screenshoteer
        and set the image to the proper field
    """
    screen_tool = getToolByName(getSite(), 'portal_screenshot')
    attrs = ['emulate', 'waitforselector', 'el', 'click', 'no', 'pdf',
             'fullPage', 'w', 'h', 'waitfor']
    default_settings = {
        'w': 1920,
        'h': 1080,
        'fullPage': 'true',
        'waitfor': 20,
        'url': url
    }
    for setting in screen_tool.objectValues():
        if setting.portal_type == obj.portal_type:
            for attr in attrs:
                if setting.getProperty(attr):
                    default_settings.update({attr: setting.getProperty(attr)})

    service_url = setting.getProperty('service_url')
    if service_url.endswith('/'):
        service_url = service_url[:-1]
    service_url += '/API/v1/retrieve_image_for_url'
    req = requests.get(service_url, stream=True, params=default_settings)
    if req.status_code == 200:
        image = Image.open(StringIO(req.content))
        destfile = StringIO()
        destfile.seek(0)
        image.save(destfile, 'JPEG')
        obj.setImage(destfile.getvalue())
        obj._p_changed = True
        obj.reindexObject()
    else:
        logger.error('Failed to set image on the following object %s' \
                     % obj.absolute_url())