""" Workflow
"""
from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.interfaces import IWorkflowEmails
from Products.Five import BrowserView


class TransitionEmails(BrowserView):
    """ Return emails for all transitions grouped in action and confirmation.
    """

    def __call__(self):
        context = self.context
        wftool = getToolByName(context, 'portal_workflow')
        workflows = wftool.getWorkflowsFor(context)
        actions = wftool.getTransitionsFor(context)
        result = {}

        for a in actions:
            for wf in workflows:
                t = wf.transitions.get(a['id'])
                if t is None:
                    continue
                emails = queryAdapter(context, IWorkflowEmails,
                                      t.new_state_id, None)
                if emails is None:
                    result[t.getId()] = 'old way (see workflow properties)'
                else:
                    result[t.getId()] = {
                        'action' : str(emails.action)[1:-1],
                        'confirmation' : str(emails.confirmation)[1:-1] }
        return result
