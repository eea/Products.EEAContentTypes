""" Send as notification """

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

class SendAsNotification(object):
    """ Send the context as email notification """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        cat = getToolByName(self.context, 'portal_catalog')
        wf = getToolByName(self.context, 'portal_workflow')
        obj_uid = self.context.UID()
        obj_id = self.context.getId()
        obj_title = self.context.Title()

        #Get notification center
        #TODO: to be changed if we use multiple notification centers
        res = cat.searchResults(portal_type = 'NewsletterTheme',
                                getId='eea_main_subscription')
        notif_center = res[0].getObject()

        #Check if notification already generated
        for nl in notif_center.getNewsletters():
            relItem = getattr(nl, 'relatedItem', None)
            if relItem and obj_uid == relItem:
                status = wf.getInfoFor(nl, 'review_state', None)
                if status == 'published':
                    status = \
                     '<span style="color:green">notification was sent</span>'
                else:
                    status = \
                     '<span style="color:red">notification not yet sent</span>'
                     
                message = u'''Email notification already generated. 
                Please check under <a title="Notification center" 
                href="%s/folder_contents">notification center</a>.
                Status: %s ''' % (notif_center.absolute_url(), status)
                
                IStatusMessage(self.request).addStatusMessage(message)
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        #Create email notification object
        notif_center.invokeFactory('Newsletter',
                                   id=obj_id,
                                   title=obj_title,
                                   relatedItem=obj_uid)
        message = u'''Email notification object created. Check under
            <a title="Notification center" href="%s/folder_contents">
            notification center</a>
             if you want to be sent''' % (notif_center.absolute_url())
        IStatusMessage(self.request).addStatusMessage(message)
        return self.request.RESPONSE.redirect(self.context.absolute_url())
