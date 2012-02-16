""" Event
"""
from Products.Five import BrowserView as FiveBrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
import PIL
from cStringIO import StringIO

class BrowserView(FiveBrowserView):
    """ View
    """
    def _getContext(self):
        """ Context getter
        """
        return self._context[0]

    def _setContext(self, value):
        """ Context setter
        """
        self._context = [value]
    context = property(_getContext, _setContext)

class SubmitEvent(BrowserView):
    """ Submit
    """
    def hasCanceled(self):
        """ Canceled?
        """
        if (self.request.get('portal_status_message') ==
            'Add New Item operation was cancelled.'):
            return True
        return False

    def step2(self):
        """ Step 2
        """
        context = self.context
        #enquiry =  context.UID()
        confirm = self.request.get('confirm')
        correct = self.request.get('correct')
        step2   = self.request.get('step2')

        if (confirm is None) and (correct is None) and (step2 is not None):
            #initial save
            return (self.request.response.redirect(context.absolute_url() +
                    '/quickevent_view?step2=on'))

        if self.request.get('confirm', None) is not None:
            workflow = getToolByName(context, 'portal_workflow')
            workflow.doActionFor(context, 'submit')
            return (self.request.response.redirect( context.absolute_url()
                                            + '/event_submitted_confirmation'))

        if self.request.get('correct', None) is not None:
            return (self.request.response.redirect( context.absolute_url()
                                                    + '/edit'))

    def canView(self):
        """ Can view
        """
        context = self.context

        mb = getToolByName(context, 'portal_membership')
        if 'Manager' in mb.getAuthenticatedMember().getRoles():
            return True

        wf = getToolByName(context, 'portal_workflow')
        state = wf.getInfoFor(context, 'review_state')
        if state == 'published':
            return True
        return False

def imageRatioCheck(obj, event):
    """ Checks if the object's image has the right 16:9 proportions and prompt
    an error message with a link if the image has wrong proportions
    """

    img = obj.getImage()
    img_size = img.getSize()

    # check if img_size isn't tuple since getSize could return the size of 
    # the image in kb
    if type(img_size) != tuple:
        orig_img = StringIO(img.data)
        image = PIL.Image.open(orig_img)
        img_size = image.size

    if img_size[0] != 0:
        ratio = float(img_size[0]) / float(img_size[1])
        if (ratio < 1.77 or ratio > 1.78):
            msg = "The image ratio is not correct, please click here to" + \
                " <a href=" + obj.absolute_url() + \
                '/crop'">Correct the image ratio</a>"
            IStatusMessage(obj.REQUEST).addStatusMessage(msg, type='error')
