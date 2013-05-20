""" CFT
"""
from Products.Five import BrowserView

class CFTRegistration(BrowserView):
    """ CFT
    """
    canView = True

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def hasCanceled(self):
        """ Canceled
        """
        if (self.request.get('portal_status_message') ==
            'Add New Item operation was cancelled.'):
            return True
        return False

    def getAwardNotice(self):
        """ Award notice
        """
        context = self.context
        awardNotice = context.getAwardNoticeObject()
        if awardNotice is not None and awardNotice != context:
            return { 'url' : awardNotice.absolute_url(),
                     'title' : awardNotice.Title() }
        return None
