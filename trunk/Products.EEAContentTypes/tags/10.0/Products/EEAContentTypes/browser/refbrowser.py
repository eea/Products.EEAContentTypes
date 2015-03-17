""" Ref browser
"""
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Acquisition import aq_parent, aq_inner

class ReferenceBrowserView(object):
    """ Provides data for referencebrowser_popup.pt """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def at_obj(self):
        """ Obj
        """
        at_url = self.request.get('at_url', '')
        obj = self.context.unrestrictedTraverse(at_url)
        return obj

    def breadcrumbs(self):
        """ Breadcrumbs
        """
        breadcrumbs = []
        obj = self.context

        while obj.portal_type != 'Plone Site':
            item = { 'Title': obj.Title(),
                     'absolute_url': obj.absolute_url() }
            breadcrumbs.insert(0, item)
            obj = aq_parent(aq_inner(obj))

        return breadcrumbs

    def contents(self):
        """ Contents
        """
        # Returns content that should be listed
        if self.context.portal_type == 'Topic':
            contents = [brain.getObject() for brain
                        in self.context.queryCatalog()]
        else:
            contents = self.context.listFolderContents()
        return contents

class ReferenceBrowserWidgetSupport(BrowserView):
    """ Support for ATReferenceBrowserWidget
    """
    def brain(self, uid):
        """ Get catalog brain by given uid
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool.unrestrictedSearchResults(UID=uid, show_inactive=True)
        for brain in brains:
            return brain
        return None
