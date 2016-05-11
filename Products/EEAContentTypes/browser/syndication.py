""" Syndication
"""
import time
from rfc822 import formatdate

from Products.CMFPlone.browser.syndication.views import FeedView
from Products.CMFPlone.interfaces.syndication import IFeedSettings
from zope.component import queryMultiAdapter


class SKOS(object):
    """ Browser view for generating a SKOS feed from an ATTopic. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def concepts(self):
        """ Concepts
        """
        synUtils = self.context.restrictedTraverse('@@syndication-util')
        maxs = self.request.get('size', None)
        if maxs is None:
            maxs = synUtils.max_items()
        else:
            maxs = int(maxs)

        brains = self.context.queryCatalog(sort_limit=maxs)[:maxs]
        objs = [brain.getObject() for brain in brains]
        objects = [obj for obj in objs if obj is not None]

        concepts = []
        for obj in objects:
            # get all translations that are available for this object
            # translations are of the form { language: [object, wf_state] }
            languages = obj.getTranslations()

            prefLabels = []
            for lang, obj_list in languages.items():
                prefLabel = {'language': lang,
                             'title': obj_list[0].Title()}
                prefLabels.append(prefLabel)

            concept = {'url': obj.absolute_url(),
                       'prefLabels': prefLabels,
                       'definition': obj.Description()}
            concepts.append(concept)

        return concepts


class EEAFeedView(FeedView):
    """ EEAFeedView
    """
    def getItemDescription(self, item):
        """ getItemDescription
        :param item: Object to get feed info
        :type item: object
        :return: Description
        :rtype: str
        """
        img = queryMultiAdapter((item.context, item.context.REQUEST),
                                name=u'imgview')
        result = item.context.Description()
        if img is not None and img.display('mini'):
            # images, highlights, press releases etc have an 'image'
            # field - if so then we show a resized version of the image
            image = img.display('mini')
            if not isinstance(image, str):
                result = '<p><img src="%s" /></p><p>%s</p>' % \
                         (img('mini').absolute_url(),
                          item.context.Description())
        return result

    def dateFormatItem(self, item):
        """
        :param item: object
        :type item: object
        :return: date formatted
        :rtype: str
        """
        date = item.published or item.modified
        date = date.asdatetime()
        return formatdate(time.mktime(date.timetuple()))

    def getViewName(self):
        """
        :return: View name
        :rtype: str
        """
        return self.__name__


class RSSUtils(object):
    """ RSSUtils #67796
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def rss2_is_enabled(self):
        """
        :return: Return boolean value if rss2 type is in feed_types
        :rtype: bool
        """
        try:
            settings = IFeedSettings(self.context)
        except TypeError:
            return False
        if settings.enabled:
            current_feeds = list(settings.feed_types)
            return u'rss.xml' in current_feeds
