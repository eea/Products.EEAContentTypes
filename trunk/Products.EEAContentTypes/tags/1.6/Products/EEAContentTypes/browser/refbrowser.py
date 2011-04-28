from Acquisition import aq_parent, aq_inner

class ReferenceBrowserView(object):
    """ Provides data for referencebrowser_popup.pt """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def at_obj(self):
        at_url = self.request.get('at_url', '')
        obj = self.context.unrestrictedTraverse(at_url)
        return obj

    def breadcrumbs(self):
        breadcrumbs = []
        obj = self.context

        while obj.portal_type != 'Plone Site':
            item = { 'Title': obj.Title(),
                     'absolute_url': obj.absolute_url() }
            breadcrumbs.insert(0, item)
            obj = aq_parent(aq_inner(obj))

        return breadcrumbs

    def contents(self):
        """ Returns content that should be listed. """
        if self.context.portal_type == 'Topic':
            contents = [brain.getObject() for brain in self.context.queryCatalog()]
        else:
            contents = self.context.listFolderContents() 
        return contents
