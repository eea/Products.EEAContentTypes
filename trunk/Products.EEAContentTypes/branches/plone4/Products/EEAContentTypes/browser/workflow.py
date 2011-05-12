#from zope.interface import implements
from zope.component import queryAdapter
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.interfaces import IWorkflowEmails

class TransitionEmails(object):
    """ Return emails for all transitions grouped in action and confirmation. """
    
    def __init__(self, context, request):
        self.context = [context]
        self.request = request

    def __call__(self):
        context = self.context[0]
        wf = getToolByName(context, 'portal_workflow')
        actions = wf.getActionsFor(context)
        result = {}

        for a in actions:
            t = a.get('transition', None)
            if t is None:
                continue
            emails = queryAdapter(context, IWorkflowEmails, t.new_state_id, None)
            if emails is None:
                result[t.getId()] = 'old way (see workflow properties)'
            else:
                result[t.getId()] = {'action' : str(emails.action)[1:-1],
                                     'confirmation' : str(emails.confirmation)[1:-1] }
        return result
