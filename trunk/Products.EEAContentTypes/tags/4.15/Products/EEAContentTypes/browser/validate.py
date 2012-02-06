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

class CFTRequestorValidator(BrowserView):
    """ CFT Validator
    """
    def validate(self):
        """ Validate
        """
        context = self.context
        errors = {}
        context.Schema().validate(context, None, errors, 1, 1)
        if errors:
            return False
        return True
