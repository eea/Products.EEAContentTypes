""" Event
"""

from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.event import ATEvent
from Products.Archetypes.atapi import Schema, registerType
from Products.Archetypes.ExtensibleMetadata import ExtensibleMetadata
from Products.CMFCore.permissions import ModifyPortalContent
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.ThemeTaggable import ThemeTaggable
from eea.locationwidget.locationwidget import LocationWidget
from eea.themecentre.interfaces import IThemeTagging
from Products.EEAContentTypes.content.interfaces import IQuickEvent
from zExceptions import NotFound
import zope.interface

QuickEvent_schema = getattr(ATEvent, 'schema', Schema(())).copy() + \
                    getattr(ThemeTaggable, 'schema', Schema(())).copy()

QuickEvent_schema.delField('text')
QuickEvent_schema['attendees'].schemata = 'metadata'
QuickEvent_schema['eventUrl'].required = True
QuickEvent_schema['themes'].widget.description = \
        'Please choose one theme to relate with this Event. ' \
        'If none apply please select default.'
QuickEvent_schema['themes'].widget.description_msgid = \
        'EEAContentTypes_help_themes_event'
QuickEvent_schema['themes'].widget.maxValues = 1
QuickEvent_schema['description'].required = True

for field in ExtensibleMetadata.schema.keys() + ['excludeFromNav']:
    # plone4 we need to check for description otherwise the edit
    # widget for description is hidden when editing a quickevent
    if field != 'description':
        QuickEvent_schema[field].widget.visible = \
            {'view':'invisible', 'edit':'invisible'}

QuickEvent_schema['location'].widget = LocationWidget(
    description="Click Edit to pinpoint to event locations",
    description_msgid="help_event_location",
    label="Event Location",
    label_msgid="label_event_location",
    i18n_domain="plone")
QuickEvent_schema['location'].widget.description = (
    "Use the address to retrieve the location <em>(e.g. "
    "Kongens Nytorv 6, 1050 Copenhagen K, Denmark)</em>")
QuickEvent_schema['location'].widget.description_msgid = (
    'EEAContentTypes_help_location_event')

#TODO: these doesn't appear to have effect
QuickEvent_schema['themes'].schemata = 'default'
QuickEvent_schema['location'].schemata = 'default'
QuickEvent_schema['subject'].schemata = 'default'

class QuickEvent(ATEvent, ThemeTaggable):
    """ Quick Event content type
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(ATEvent, '__implements__', ()),)
    zope.interface.implements(IQuickEvent)

    # This name appears in the 'add' box
    archetype_name = 'QuickEvent'

    meta_type = 'QuickEvent'
    portal_type = 'QuickEvent'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'base_view'
    default_view = 'base_view'
    typeDescription = "Event submitted by public"
    typeDescMsgId = 'description_edit_quickevent'

    _at_rename_after_creation = True

    schema = QuickEvent_schema

    # fields hidden from ATEvent get dummy values and accessor/mutators for BBB
    attendees = []

    def getText(self):
        """ Get text
        """
        return ''

    def setText(self, value):
        """ Set text
        """
        self.text = value

    text = property(getText, setText)

    def getEventType(self):
        """ Get event type
        """
        return ''

    def setEventType(self, value, **kw):
        """ Set event type
        """
        pass

    eventType = property(getEventType, setEventType)

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes.
        """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value

    security.declareProtected(ModifyPortalContent, 'processForm')
    def processForm(self, data=1, metadata=0, REQUEST=None, values=None):
        """ We want to see if the form was submited by robot or not
        """
        if data:    #we're only interested in the regular edit form
            request = REQUEST or self.REQUEST
            if values:
                form = values
            else:
                form = request.form

            if not form.get("mehuman"):
                rq = self.REQUEST or REQUEST
                if not (rq['HTTP_REFERER'] and \
                        rq['HTTP_REFERER'].endswith('/properties')):
                    raise NotFound  #We're dealing with a spammer

        return ATEvent.processForm(self, data, metadata, REQUEST, values)

    def toLocalizedTime(self, time, long_format, time_only):
        return time.date()

registerType(QuickEvent, PROJECTNAME)
