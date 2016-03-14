""" Validate
"""

from Products.Five import BrowserView


class NotValid(BrowserView):
    """ Not valid
    """

    def validate(self):
        """ Validate
        """
        return False
