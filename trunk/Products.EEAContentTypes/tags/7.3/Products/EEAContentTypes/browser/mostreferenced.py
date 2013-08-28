""" Most referenced
"""
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


class MostReferenced(BrowserView):
    """ Returns the most referenced objects filtered by portal_type
        and/or interface (by both backward and forward references)
    """

    def __call__(self, count=10, portal_type=None, interface=None):
        cat = getToolByName(self.context, 'portal_catalog')
        query = {'sort_on': 'countReferences',
                 'sort_order': 'reverse',
                 'review_state':'published'}

        if portal_type:
            query['portal_type'] = portal_type
        if interface:
            query['object_provides'] = interface

        brains = cat(**query)
        return [brain.getObject() for brain in brains[:int(count)]]
