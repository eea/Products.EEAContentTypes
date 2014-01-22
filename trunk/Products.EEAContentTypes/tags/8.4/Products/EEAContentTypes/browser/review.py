""" Review
"""
from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
import logging
logger = logging.getLogger('Products.EEAContentTypes.browser.review')

class ReviewList(object):
    """ Browser view to get all pending objects. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # This is essentially a copy of
        # CMFPlone.WorkflowTool.getWorklistsResults() to fix #1115.
        # We need to add Language='all' to the catalog query

        sm = getSecurityManager()
        # We want to know which types use the workflows with worklists
        # This for example avoids displaying 'pending' of multiple
        # workflows in the same worklist
        types_tool = getToolByName(self, 'portal_types')
        wftool = getToolByName(self, 'portal_workflow')
        catalog = getToolByName(self, 'portal_catalog')

        list_ptypes = types_tool.listContentTypes()
        types_by_wf = {} # wf:[list,of,types]
        for t in list_ptypes:
            for wf in wftool.getChainFor(t):
                types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        # PlacefulWorkflowTool will give us other results
        placeful_tool = getToolByName(self, 'portal_placeful_workflow', None)
        if placeful_tool is not None:
            for policy in placeful_tool.getWorkflowPolicies():
                for t in list_ptypes:
                    chain = policy.getChainFor(t) or ()
                    for wf in chain:
                        types_by_wf[wf] = types_by_wf.get(wf, []) + [t]

        objects_by_path = {}
        for wid in wftool.getWorkflowIds():

            wf = wftool.getWorkflowById(wid)
            if hasattr(wf, 'worklists'):
                #wlists = []
                for worklist in wf.worklists._objects:
                    wlist_def = wf.worklists._mapping[worklist['id']]
                    # Make the var_matches a dict instead of PersistentMapping
                    # to enable access from scripts
                    catalog_vars = dict(portal_type=types_by_wf.get(wid, []))
                    for key in wlist_def.var_matches.keys():
                        catalog_vars[key] = wlist_def.var_matches[key]
                    catalog_vars['Language'] = 'all'
                    for result in catalog.searchResults(**catalog_vars):
                        try:
                            o = result.getObject()
                            if o \
                            and wid in wftool.getChainFor(o) \
                            and wlist_def.getGuard().check(sm, wf, o):
                                absurl = o.absolute_url()
                            if absurl:
                                objects_by_path[absurl] = (o.modified(), o)
                        except Exception, err:
                            logger.info(err)

        results = objects_by_path.values()
        results.sort()
        return tuple([ obj[1] for obj in results ])
