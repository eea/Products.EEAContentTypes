""" Custom URL normalizer
"""
import logging
from zope.interface import implements
from plone.i18n.normalizer import MAX_URL_LENGTH, FILENAME_REGEX
from plone.i18n.normalizer import urlnormalizer
from plone.i18n.normalizer.interfaces import IURLNormalizer

from Products.EEAContentTypes.config import MAX_URL_WORDS, URL_ORPHANS

logger = logging.getLogger("Products.EEAContentTypes")

class EEAURLNormalizer(object):
    """ Customize default URL normalizer
    """
    implements(IURLNormalizer)

    def normalize(self, text, locale=None, max_length=MAX_URL_LENGTH,
                  max_words=MAX_URL_WORDS, orphans=URL_ORPHANS):
        """
        Override plone.i18n URLNormalizer to accept cutting by words.
        """
        if not isinstance(text, unicode):
            try:
                text = text.decode('utf-8')
            except Exception:
                logger.info("Can't decode URL to be normalized")

        text = urlnormalizer.normalize(text, locale, max_length)
        if not max_words:
            return text

        m = FILENAME_REGEX.match(text)
        if m is not None:
            text = m.groups()[0]
            ext  = m.groups()[1]
        else:
            ext = ''

        new_text = text.split('-')
        if len(new_text) <= max_words + orphans:
            new_text = text
        else:
            new_text = '-'.join(new_text[:max_words])

        if ext:
            new_text = '.'.join((new_text, ext))
        return new_text

eeaurlnormalizer = EEAURLNormalizer()
