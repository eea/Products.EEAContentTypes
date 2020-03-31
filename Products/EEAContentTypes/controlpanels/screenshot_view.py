""" Views
"""
from Products.CMFPlone.utils import getToolByName
from Products.Five import BrowserView
from Products.statusmessages.interfaces import IStatusMessage
from Products.EEAContentTypes.controlpanels.interfaces import IScreenshotPortalType
from Products.EEAContentTypes.controlpanels.schema import PortalType
from Products.EEAContentTypes.config import EEAMessageFactory as _
from plone.api.portal import getSite
from z3c.form import form, field
from z3c.form import button


def input_is_valid(self, data):
    """ Flag input as invalid if there already exists a setting/content type
    """
    ptype = data.get('portal_type')
    screen_tool = getToolByName(getSite(), 'portal_screenshot')

    if screen_tool == self.context:
        if ptype in [obj.portal_type for obj in screen_tool.objectValues()]:
            self.status = _("There already exists a setting for the specified "
                            "portal type")
            self.formErrorsMessage = self.status
            return False
    else:
        for obj in screen_tool.objectValues():
            if ptype == obj.portal_type and self.context != obj:
                self.status = _("Cannot change portal type, there already exists "
                                "a setting for the specified portal type")
                self.formErrorsMessage = self.status
                return False
    return True


class ScreenshotToolView(BrowserView):
    """ Browser view for eea versions tool
    """
    def add(self):
        """ Add new portal type
        """
        if not self.request:
            return None
        self.request.response.redirect('@@add')

    def delete(self, **kwargs):
        """ Delete portal types
        """
        ids = kwargs.get('ids', [])
        msg = self.context.manage_delObjects(ids)
        if not self.request:
            return msg
        self.request.response.redirect('@@view')

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request)

        if kwargs.get('form.button.Add', None):
            return self.add()
        if kwargs.get('form.button.Delete', None):
            return self.delete(**kwargs)
        return self.index()


class AddPage(form.AddForm):
    """ Add page
    """
    fields = field.Fields(IScreenshotPortalType)

    def create(self, data):
        """ Create
        """
        valid_input = input_is_valid(self, data)
        if not valid_input:
            return
        ob = PortalType(id=data.get('title', 'ADDTitle'))
        form.applyChanges(self, ob, data)
        return ob

    def add(self, obj):
        """ Add
        """
        if not obj:
            return
        name = obj.getId()
        self.context[name] = obj
        self._finished_add = True
        return obj

    def nextURL(self):
        """ Next
        """
        return "./@@view"


class EditPage(form.EditForm):
    """ Edit page
    """
    fields = field.Fields(IScreenshotPortalType)

    def nextURL(self):
        """ Next
        """
        return "../@@view"

    @button.buttonAndHandler(_(u"label_apply", default=u"Apply"),
                             name='apply')
    def handleApply(self, action):
        """ Apply button
        """
        data = self.extractData()[0]
        valid_input = input_is_valid(self, data)
        if not valid_input:
            return
        super(EditPage, self).handleApply(self, action)
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        """ Cancel button
        """
        self.request.response.redirect(self.nextURL())
        return ''
