""" EEAVersions Tool
"""
from zope.component import queryMultiAdapter
from zope.interface import implements
from OFS.Folder import Folder
from Products.CMFCore.utils import getToolByName
from BTrees.IIBTree import IIBucket

from Products.EEAContentTypes.controlpanels.interfaces import IScreenshotTool
from Products.EEAContentTypes.controlpanels.interfaces import IScreenshotCatalog


class ScreenshotTool(Folder):
    """ A local utility storing all screenshot global settings """
    implements(IScreenshotTool)

    id = 'portal_screenshot'
    title = 'Manages screenshot global settings'
    meta_type = 'EEA Screenshot Tool'

    def apply_index(self, index, value):
        """ Custom catalog apply_index method
        """
        ctool = getToolByName(self, 'portal_catalog')
        catalog = queryMultiAdapter((self, ctool), IScreenshotCatalog)
        if not catalog:
            return IIBucket(), (index.getId(),)
        return catalog.apply_index(index, value)

    def search(self, **query):
        """
        Use this method to search over catalog using defined
            screenshot portal types.
        """
        ctool = getToolByName(self, 'portal_catalog')
        catalog = queryMultiAdapter((self, ctool), IScreenshotCatalog)
        if not catalog:
            return ctool(**query)
        return catalog(**query)
