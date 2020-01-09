""" Control panel
"""
import logging
import pytz
import datetime
from zope.interface import Interface, implements
from zope.component import queryUtility
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.EEAContentTypes.async import IAsyncService
from plone.app.layout.viewlets.content import ContentHistoryView


class IStatusExpirationDate(Interface):
    """ Expiration Date Status Interface
    """

    def startFixExpirationDate(self):
        """ Fix affected objects
        """

    def scheduleFixExpirationDate(self):
        """ Schedule fix to zc.async queue
        """


class StatusExpirationDate(BrowserView):
    """ Expiration Date Status
    """

    implements(IStatusExpirationDate)
    index = ViewPageTemplateFile("status_expirationdate.pt")

    def __init__(self, context, request):
        super(StatusExpirationDate, self).__init__(context, request)
        self.logger = logging.getLogger(
            "ExpirationFix")

    def search(self, filters=None):
        """ Search objs without expiration date
        """
        result = []

        log = logging.getLogger("ExpirationDate status:")
        catalog = getToolByName(self.context, 'portal_catalog')
        query = {
#            'review_state': "published",
            'Language': "all",
            'show_inactive': True,
            'object_provides': ['eea.workflow.interfaces.IObjectArchived']
        }

        if filters:
            query.update(filters)

        log.info("Catalog search start")
        brains = catalog.searchResults(**query)
        log.info("Catalog search ended")

        for brain in brains:
            if brain.ExpirationDate == 'None':
                result.append(brain)

        if result:
            log.warning(
                "Found %s affected objects", len(result)
            )
        else:
            log.info("Objects already DONE")

        return result

    def __call__(self):
        return self.index()

    def getExpirationDateStatus(self):
        """ Returns the view's main output; getter for
            'self.brains'
        """
        return [{
            'url': b.getURL(),
            'id': b.getId,
            'title': b.Title,
            'type': b.portal_type,
        } for b in self.search()]

    def startFixExpirationDate(self):
        """ Fix affected objects
        """
        wf = getToolByName(self.context, "portal_workflow", None)
        mt = getToolByName(self.context, 'portal_membership', None)
        actor = mt.getAuthenticatedMember().id

        for brain in self.search():
            obj = brain.getObject()
            history = ContentHistoryView(obj, self.request).fullHistory()
            for entry in history:
                if entry['transition_title'] == 'Archive':
                    date = entry['time']
                    obj.setExpirationDate(date)
                    for wfname in obj.workflow_history.keys():
                        state = wf.getInfoFor(obj, 'review_state', 'None')
                        comment = 'Added missing Expiration Date.'
                        history = obj.workflow_history[wfname]
                        history += ({
                                        'action': 'Upgrade script',
                                        'review_state': state,
                                        'actor': actor,
                                        'comments': comment,
                                        'time': DateTime(),
                                    },)
                        obj.workflow_history[wfname] = history
                    obj.workflow_history._p_changed = True
                    obj.reindexObject()
                    notify(ObjectModifiedEvent(obj))
                    break
        start = self.request.get('start_from_script', None)
        if start:
            return

        return self.index()

    def scheduleFixExpirationDate(self):
        """ Schedule fix to zc.async
        """
        async = queryUtility(IAsyncService)
        if async is not None:
            queue = async.getQueues()['']
            async.queueJobInQueue(
                queue, ('ctypes',),
                fix_expiration_date,
                self.context
            )
        else:
            fix_expiration_date(self.context)
        return "OK"


def fix_expiration_date(context):
    """ Fix ExpirationDate asynchronously
    """
    async = queryUtility(IAsyncService)
    if async is not None:
        delay = datetime.timedelta(days=1)
        queue = async.getQueues()['']
        async.queueJobInQueueWithDelay(
            None, datetime.datetime.now(pytz.UTC) + delay,
            queue, ('ctypes',),
            fix_expiration_date,
            context
        )
