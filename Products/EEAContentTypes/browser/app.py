from Products.Five import BrowserView
from RestrictedPython.Utilities import same_type


class UnicodeTestIn(BrowserView):
    """A faster replacement for unicodeTestIn.py from Archetypes
    """

    def __call__(self, value, vocab):
        """ call
        """
        if vocab is None or len(vocab) == 0:
            return 0

        value = self.unicodeEncode(value)
        for v in vocab:
            if self.unicodeEncode(v) == value:
                return True

        return False

    def unicodeEncode(self, value, site_charset=None):
        """ unicodeEncode
        """

        # Recursively deal with sequences
        tuplevalue = same_type(value, ())
        if (tuplevalue or same_type(value, [])):
            encoded = [self.unicodeEncode(v) for v in value]
            if tuplevalue:
                encoded = tuple(encoded)
            return encoded

        if not isinstance(value, basestring):
            value = str(value)

        if site_charset is None:
            site_charset = self.context.getCharset()

        if same_type(value, ''):
            value = unicode(value, site_charset)

        # don't try to catch unicode error here
        # if one occurs, that means the site charset must be changed !
        return value.encode(site_charset)

