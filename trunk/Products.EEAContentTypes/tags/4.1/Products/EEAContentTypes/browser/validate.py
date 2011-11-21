#import zope.interface

from Products.Five import BrowserView

class NotValid(BrowserView):

    def validate(self):
        return False

class CFTRequestorValidator(BrowserView):

    def validate(self):
        context = self.context
        errors = {}
        context.Schema().validate(context, None, errors, 1, 1)
        if errors:
            return False
        return True

        
