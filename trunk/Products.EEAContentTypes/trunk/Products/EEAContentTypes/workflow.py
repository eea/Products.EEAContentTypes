""" Workflow
"""
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import ILocalRoleEmails
from Products.EEAContentTypes.interfaces import ITransitionLogicalGuard
from Products.EEAPloneAdmin.interfaces import IWorkflowEmails
from zope.component import adapts, queryAdapter
from zope.interface import implements, Interface

class TransitionLogicalGuard(object):
    """ get right transition logic adapter for the context and transition """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        state_change = self.context
        guard = queryAdapter(state_change.object,
                ITransitionLogicalGuard, name=state_change.transition.getId())
        if guard is not None:
            return guard.available
        return True


class SubmitForWebQAGuard(object):
    """ guard for transition """

    implements(ITransitionLogicalGuard)

    notNeededFor = [ 'Link' ]
    needContentReview = [ 'Event', 'Document', 'News Item', 'Highlight' ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        portal_type = context.portal_type
        if portal_type not in self.notNeededFor:
            if portal_type in self.needContentReview:
                wf = getToolByName(context, 'portal_workflow')
                history = [ h['action'] for
                            h in (wf.getInfoFor(context,
                                               'review_history', None) or [])]
                return 'submitContentReview' in history
            return True
        return False


class SubmitForMultimediaEdit(object):
    """ guard for transition """

    implements(ITransitionLogicalGuard)

    canBeUsedFor = [ 'Highlight', 'PressRelease', 'Document', 'News Item',
                     'HelpCenterFAQ', 'Speech', 'Topic']

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context
        wf = getToolByName(context, 'portal_workflow')
        history = [ h['action'] for
                    h in wf.getInfoFor(context, 'review_history', None) ]
        return (self.context.portal_type
                in self.canBeUsedFor and 'submitMultimediaEdit' not in history)


class SubmitForContentReview(object):
    """ guard for transition """

    implements(ITransitionLogicalGuard)

    canBeUsedFor = [ 'Highlight', 'Document', 'News Item', 'HelpCenterFAQ',
                     'Topic', 'Event', 'Link']

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.context.portal_type in self.canBeUsedFor


class SubmitForProofReading(object):
    """ guard for transition """

    implements(ITransitionLogicalGuard)

    canBeUsedFor = [ 'Highlight', 'Document', 'HelpCenterFAQ' ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.context.portal_type in self.canBeUsedFor


class QuickPublish(object):
    """ guard for transition """

    implements(ITransitionLogicalGuard)

    canBeUsedFor = [ 'Link' ]

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        return self.context.portal_type in self.canBeUsedFor


class LocalRoleEmails(object):
    """ Email
    """
    implements(ILocalRoleEmails)
    adapts(Interface)

    emails = {}

    def __init__(self, context):
        self.context = context
        self.emails = {}
        self.takenRoles = []
        self.existing_role_settings()

    def existing_role_settings(self):
        """  from computeRoleMap.py
        """
        context = self.context

        # we call the _getLocalRolesForDisplay instead of
        # getLocalRolesForDisplayand to avoid security check to allow all roles
        # subpmit emails on workflow submition
        local_roles = context.acl_users._getLocalRolesForDisplay(context)

        # first process local roles
        self._parseRoles(local_roles)

        # second process acquired roles
        acquired_roles = self.getInheritedLocalRoles(context)
        self._parseRoles(acquired_roles)

        # and last global roles
        self._parseRoles(self.getGlobalRoles())

    def _parseRoles(self, roles):
        """ Roles
        """
        context = self.context
        mtool = context.portal_membership
        gtool = getToolByName(context, 'portal_groups')

        for name, roles, utype, uid in roles:
            if not uid.startswith('group_') and utype == 'user':
                member = mtool.getMemberById(name)
                if member is not None:
                    email = member.getProperty('email')
                    if email:
                        for role in roles:
                            roleEmails = self.emails.get(role, [])
                            if email not in roleEmails:
                                roleEmails.append(email)
                            self.emails[role] = roleEmails
            else:
                grp = gtool.getGroupById(uid)
                members = grp.getGroupMembers()
                for role in roles:
                    roleEmails = self.emails.get(role, [])
                    for m in members:
                        email = m.getProperty('email')
                        if email not in roleEmails:
                            roleEmails.append(email)
                    self.emails[role] = roleEmails

    def getInheritedLocalRoles(self, here):
        """Returns a tuple with the acquired local roles."""
        portal = getToolByName(here, 'portal_url').getPortalObject()
        pu = getToolByName(here, 'plone_utils')
        result = []
        takenRoles = self.takenRoles
        cont = 1
        if portal != here:
            parent = here.aq_parent
            while cont:
                if not getattr(here, 'acl_users', False):
                    break
                userroles = here.acl_users._getLocalRolesForDisplay(parent)
                rolesOnCurrentParent = []
                for user, roles, role_type, name in userroles:
                    # Find user in result
                    found = 0

                    tmpRoles = []
                    for role in roles:
                        if role not in takenRoles:
                            tmpRoles.append(role)
                            if role not in rolesOnCurrentParent:
                                rolesOnCurrentParent.append(role)

                    if not tmpRoles:
                        # no new roles
                        continue
                    roles = tmpRoles

                    for user2, roles2, _type2, _name2 in result:
                        if user2 == user:
                            # Check which roles must be added to roles2
                            for role in roles:
                                if role not in roles2:
                                    roles2.append(role)
                            found = 1
                            break
                    if found == 0:
                        # Add it to result and make sure roles is a list so
                        # we may append and not overwrite the loop variable
                        result.append([user, list(roles), role_type, name])

                # parent done, append taken roles
                takenRoles.extend(rolesOnCurrentParent)

                if parent == portal:
                    cont = 0
                elif not pu.isLocalRoleAcquired(parent):
                    # Role acquired check here
                    cont = 0
                else:
                    parent = parent.aq_parent

        # Tuplize all inner roles
        for pos in range(len(result) - 1, -1, -1):
            result[pos][1] = tuple(result[pos][1])
            result[pos] = tuple(result[pos])

        self.takenRoles = takenRoles
        return tuple(result)

    def getGlobalRoles(self):
        """ Global roles
        """
        context = self.context
        groups_tool = getToolByName(context, 'portal_groups')
        members_tool = getToolByName(context, 'portal_membership')
        retlist = []
        takenRoles = self.takenRoles
        for member in members_tool.searchForMembers():
            roles = [ role for role in member.getRoles()
                           if role not in takenRoles ]
            if roles:
                retlist.append((member.getUserName(), roles,
                                'user', member.getUserId()))

        for grpId in groups_tool.getGroupIds():
            group = groups_tool.getGroupById(grpId)
            roles = [ role2 for role2 in group.getRoles()
                           if role2 not in takenRoles ]
            if roles:
                retlist.append((group.getGroupName(), roles,
                                'group', group.getGroupName()))

        return retlist


class WorkflowEmails(object):
    """ Workflow emails
    """
    implements(IWorkflowEmails)
    adapts(Interface)

    action = []
    confirmation = []

    def __init__(self, context):
        self.context = context
        self.action = []
        self.confirmation = []

    def _getEmails(self, actionRole):
        """ Emails
        """
        context = self.context
        local = ILocalRoleEmails(context)
        self.action = local.emails.get(actionRole, [])

        # confirmation is sent to all roles except actionRoles
        confirmationRoles = [
            role for role in ('ContentManager', 'Editor',
                              'Reviewer', 'WebReviewer', 'Owner', 'Manager')
            if role != actionRole ]
        for role in confirmationRoles:
            emails = local.emails.get(role, [])
            for email in emails:
                if email not in self.action and email not in self.confirmation:
                    self.confirmation.append(email)

    @property
    def sender(self):
        """ Sender
        """
        portal = self.context.portal_url.getPortalObject()
        mt = getToolByName(self.context, 'portal_membership')
        member = mt.getAuthenticatedMember()
        name = portal.email_from_name
        email = portal.email_from_address
        if member is not None:
            memberEmail = member.getProperty('email', None)
            memberName = member.getProperty('fullname',
                                            '') or memberEmail.replace('@', ' ')
            if memberEmail and memberName:
                email = memberEmail
                name = memberName

        return "%s <%s>" % (name, email)


#TODO: We need to make the Roles in each workflow adpater to take it dynamically
# from the actual workflow object roles guard. This way we skip hardcoded values
# and we can reuse the workflow sendemail logic for all workflows.
class WorkflowActionReviewer(WorkflowEmails):
    """ Action reviewer
    """
    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('Reviewer')


class WorkflowActionProofReader(WorkflowEmails):
    """ Proof reader
    """
    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('ProofReader')


class WorkflowActionWebReviewer(WorkflowEmails):
    """ Web reviewer
    """
    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('WebReviewer')


class WorkflowActionEditor(WorkflowEmails):
    """ Used for state new """

    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('Editor')


class WorkflowActionContentManager(WorkflowEmails):
    """ Used when sent back for revision. """

    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('ContentManager')


class WorkflowConfirmation(WorkflowEmails):
    """ This will send a workflow confirmation email to all roles"""
    def __init__(self, context):
        WorkflowEmails.__init__(self, context)
        self._getEmails('')
