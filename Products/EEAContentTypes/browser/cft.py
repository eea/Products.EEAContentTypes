import zope.interface
import zope.component

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class CFTRegistration(BrowserView):

    canView = True
    
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def hasCanceled(self):
        if self.request.get('portal_status_message') == 'Add New Item operation was cancelled.':
            return True
        return False
    
    def getAwardNotice(self):
        context = self.context
        awardNotice = context.getAwardNoticeObject()
        if awardNotice is not None and awardNotice != context:
            return { 'url' : awardNotice.absolute_url(),
                     'title' : awardNotice.Title() }
        return None
    
