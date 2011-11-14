#import zope.interface
#import zope.component

from Products.Five import BrowserView as FiveBrowserView
from Products.CMFCore.utils import getToolByName

class BrowserView(FiveBrowserView):

    def _getContext(self):
        return self._context[0]
    def _setContext(self, value):
        self._context = [value]
    context = property(_getContext, _setContext)
        
class SubmitEvent(BrowserView):

    def hasCanceled(self):
        if self.request.get('portal_status_message') == 'Add New Item operation was cancelled.':
            return True
        return False

    def step2(self):
        context = self.context
        #enquiry =  context.UID()

        if self.request.get('confirm', None) is not None:
            workflow = getToolByName(context, 'portal_workflow')
            workflow.doActionFor(context, 'submit')
            return self.request.response.redirect( context.absolute_url() + '/event_submitted_confirmation')
                                                   
        if self.request.get('correct', None) is not None:
            return self.request.response.redirect( context.absolute_url() + '/edit')

    def canView(self):
        context = self.context

        mb = getToolByName(context, 'portal_membership')
        if 'Manager' in mb.getAuthenticatedMember().getRoles():
            return True

        wf = getToolByName(context, 'portal_workflow')
        state = wf.getInfoFor(context, 'review_state')
        if state == 'published':
            return True
        return False
