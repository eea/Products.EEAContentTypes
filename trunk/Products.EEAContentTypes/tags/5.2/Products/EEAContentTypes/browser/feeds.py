""" Feeds
"""
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from eea.rdfrepository.utils import getRdfPortletData
from plone.app.layout.navigation.interfaces import INavigationRoot


class RDFPortlet(object):
    """ Feeds
    """
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        portal_url = getToolByName(self.context, 'portal_url')
        portal = portal_url.getPortalObject()
        obj = self.context
        while not (INavigationRoot.providedBy(obj) and
                   aq_base(obj) is not aq_base(portal)):
            obj = utils.parent(obj)

        return getRdfPortletData(obj, max_items=3)
