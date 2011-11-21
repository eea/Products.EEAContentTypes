""" Send as notification """

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

class SendAsNotification(object):
    """ Send the context as email notification """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        pu = getToolByName(self.context, 'plone_utils')
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
                message = _((
                    u'Email notification already generated. Please check under '
                    '<a title="Notification center" href="${url}/'
                    'folder_contents">notification center</a>. '
                    'Status: ${status}'),
                            mapping = {u'url' : notif_center.absolute_url(),
                                       u'status' : status})
                pu.addPortalMessage(message, 'structure')
                return self.request.RESPONSE.redirect(
                    self.context.absolute_url())

        #Create email notification object
        notif_center.invokeFactory('Newsletter',
                                   id=obj_id,
                                   title=obj_title,
                                   relatedItem=obj_uid)
        message = _((
            u'Email notification object created. Check under '
            '<a title="Notification center" href="${url}/folder_contents">'
            'notification center</a> if you want to be sent'),
                    mapping={u'url' : notif_center.absolute_url()})
        pu.addPortalMessage(message, 'structure')
        return self.request.RESPONSE.redirect(self.context.absolute_url())
