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
from Products.EEAContentTypes.config import EEAMessageFactory as _

def purge(obj):
    """ Purge object
    """
    if isPurged(obj):
        notify(Purge(obj))

class InvalidateCache(BrowserView):
    """ Invalidate cache
    """
    def __init__(self, context, request):
        super(InvalidateCache, self).__init__(context, request)
        self.parent = context
        if utils.isDefaultPage(context, request):
            self.parent  = aq_parent(aq_inner(context))

    def _redirect(self, msg='', mtype=u'info'):
        """ Return with status message
        """
        if msg:
            IStatusMessage(self.request).addStatusMessage(msg, mtype)
        self.request.response.redirect(self.parent.absolute_url())
        return msg

    def can_invalidate(self):
        """ Current user can invalidate cache
        """
        # Don't allow invalidation with direct link
        referer =  self.request.get('HTTP_REFERER', '')
        if referer.endswith('/'):
            referer = referer[:-1]
        if (self.context.absolute_url() != referer and
            self.parent.absolute_url() != referer):
            return False

        # Authenticated editors can invalidate cache from everywhere
        mtool = getToolByName(self.context, 'portal_membership')
        if mtool.checkPermission('Modify portal content', self.parent):
            return True

        # Check eea internal ips
        addr_list = set(['127.0.0.1'])
        ptool = getToolByName(self.context, 'portal_properties')
        ips_list = getattr(ptool, 'eea_internal_ips', None)
        if ips_list:
            addr_list.update(ips_list.getProperty('allowed_ips', []))

        addr = self.request.get('HTTP_X_FORWARDED_FOR', '')
        addr = addr or self.request.get('REMOTE_ADDR', '')

        for ip in addr_list:
            if addr.startswith(ip):
                return True
        return False

    def invalidate(self):
        """ Invalidate cache
        """
        if not self.can_invalidate():
            msg = _(u'You are not allowed to invalidate cache in this context')
            self.request.response.setStatus(401, msg)
            return self._redirect(msg, u'error')

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
            if self.context != self.parent:
                purge(self.parent)

        return self._redirect(_(u'Request for cache invalidation sent'))
