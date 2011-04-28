import transaction

SAVE_THRESHOLD = 100 # Do a savepoint every so often
_marker = object()

from Products.CMFCore.utils import getToolByName
from Globals import PersistentMapping
from Acquisition import aq_base
from DateTime import DateTime

def remap_workflow(context, type_ids, chain, state_maps={}, workflows={}):
    """Change the workflow for each type in type_ids to use the workflow
    chain given. state_map is a dictionary of old state names to
    new ones. States that are not found will be remapped to the default
    state of the new workflow.
    """
    
    if chain is None:
        chain = '(Default)'

    portal_workflow = getToolByName(context, 'portal_workflow')
    chain_workflows = {}

    new_wf = portal_workflow.eea_default_workflow
    portal_catalog = getToolByName(context, 'portal_catalog')
    
    # Then update the state of each
    remapped_count = 0
    threshold_count = 0
    for brain in portal_catalog(portal_type=type_ids, Language='all'):
        obj = brain.getObject()
        
        # Work out what, if any, the previous state of the object was
        portal_type = brain.portal_type
        old_wf = workflows.get(brain.portal_type, portal_workflow.plone_workflow )

        # ignore objects that already use new workflow
        new_wf = portal_workflow.eea_default_workflow        
        new_status = portal_workflow.getHistoryOf(new_wf.getId(), obj)
        if new_status is not None:
            continue
        
        old_state = None
        if old_wf is not None:
            old_status = portal_workflow.getHistoryOf(old_wf.getId(), obj)
            if old_status is not None:
                old_state = old_status[-1].get('review_state', None)
            
        # Now add a transition
        state_map = state_maps.get(brain.portal_type, state_maps['default'])
        new_wf_name = 'eea_default_workflow'
        new_status = { 'action'       : None,
                       'actor'        : None, 
                       'comments'     : 'State remapped from control panel',
                       'review_state' : state_map.get(old_state, new_wf.initial_state),
                       'time'         : DateTime()}

        portal_workflow.setStatusOf(new_wf_name, obj, new_status)
        new_wf.updateRoleMappingsFor(obj)
        obj.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
        
        remapped_count += 1
        threshold_count += 1
        
        if threshold_count > SAVE_THRESHOLD:
            transaction.savepoint()
            threshold_count = 0
            
    return remapped_count
