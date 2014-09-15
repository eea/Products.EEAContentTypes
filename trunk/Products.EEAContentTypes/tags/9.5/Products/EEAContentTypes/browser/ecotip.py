""" Ecotip
"""
import random
from Products.CMFCore.utils import getToolByName

class RandomEcotip(object):
    """ Returns a random ecotip. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        brains = catalog.searchResults(portal_type='EcoTip',
                                       review_state='published')
        if brains:
            rand = random.randint(0, len(brains)-1)
            brain = brains[rand]

            return { 'title': brain.Title,
                     'description': brain.Description,
                     'url': brain.getURL() }
        else:
            return None
