""" EEAContentTypes actions for plone.app.contentrules
"""

from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IExecutable, IRuleElementData
from zope import schema
from zope.component import adapts, getUtility
from zope.formlib import form
from zope.interface import implements, Interface
import logging

logger = logging.getLogger("Producs.EEAContentTypes.actions")


class IEnableDisableDiscussionAction(Interface):
    """ Enable/Disable Discussion settings schema
    """
    action = schema.Choice(title=u"How discussions are changed",
                  description=u"Should the discussions be disabled or enabled?",
                  values=['enabled', 'disabled'],
                  required=True)


class EnableDisableDiscussionAction(SimpleItem):
    """ Enable/Disable Discussion Action settings
    """
    implements(IEnableDisableDiscussionAction, IRuleElementData)

    element = 'Products.EEAContentTypes.actions.EnableDisableDiscussion'
    action = None #default value

    def summary(self):
        if self.action:
            return "Discussions will be %s"  % self.action
        else:
            return "Not configured"



class EnableDisableDiscussionActionExecutor(object):
    """ Enable/Disable Discussion Action executor
    """
    implements(IExecutable)
    adapts(Interface, IEnableDisableDiscussionAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        container = self.context
        event = self.event
        action = self.action
        obj = self.event.object

        choice = {'enabled':1, 'disabled':0}.get(action.action)
        if choice is not None:
            obj.allowDiscussion(choice)
            logger.info("Discussions for %s set to %s", obj.absolute_url(), 
                                                   action.action)
        else:
            logger.info("Products.EEAContentTypes.actions.EnableDisableDisc"
                        "ussion action is not properly configured")

        return True


class EnableDisableDiscussionAddForm(AddForm):
    """ Enable/Disable Discussion addform
    """
    form_fields = form.FormFields(IEnableDisableDiscussionAction)
    label = u"Add Enable/Disable Discussion Action"
    description = u"A Enable/Disable Discussion action."
    form_name = u"Configure element"

    def create(self, data):
        """ create method
        """
        a = EnableDisableDiscussionAction()
        form.applyChanges(a, self.form_fields, data)
        return a


class EnableDisableDiscussionEditForm(EditForm):
    """ Enable/Disable Discussion editform
    """
    form_fields = form.FormFields(IEnableDisableDiscussionAction)
    label = u"Edit Enable/Disable Discussion Action"
    description = u"A Enable/Disable Discussion action."
    form_name = u"Configure element"

