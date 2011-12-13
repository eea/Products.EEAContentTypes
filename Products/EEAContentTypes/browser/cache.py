""" Cache
"""
from zope.event import notify
from plone.app.caching.utils import isPurged
from z3c.caching.purge import Purge

from Acquisition import aq_parent, aq_inner
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.statusmessages.interfaces import IStatusMessage

def purge(obj):
    """ Purge object
    """
    if isPurged(obj):
        notify(Purge(obj))

class InvalidateCache(BrowserView):
    """ Invalidate cache
    """
    def invalidate(self):
        """ Invalidate cache
        """
        parent = self.context
        if utils.isDefaultPage(self.context, self.request):
            parent  = aq_parent(aq_inner(self.context))

        recursive = self.request.get('recursive_invalidation' , False)
        if recursive:
            path = '/'.join(self.context.getPhysicalPath())
            cat = getToolByName(self.context, 'portal_catalog')
            brains = cat(path=path)
            for brain in brains:
                doc = brain.getObject()
                purge(doc)
        else:
            purge(self.context)
            if self.context != parent:
                purge(parent)

        IStatusMessage(self.request).addStatusMessage(
            'Request for cache invalidation sent',
            type='info')
        self.request.response.redirect(parent.absolute_url())
        return 'Request for cache invalidation sent'
