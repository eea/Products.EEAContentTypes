""" Speech """
from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import (Schema, BaseSchema, BaseContent,
        registerType)
from Products.EEAContentTypes.content.Highlight import Highlight
from Products.EEAContentTypes.config import PROJECTNAME
from Products.CMFCore.permissions import ModifyPortalContent
from eea.themecentre.interfaces import IThemeTagging

schema = Schema((

),
)

Speech_schema = BaseSchema.copy() + \
    getattr(Highlight, 'schema', Schema(())).copy() + \
    schema.copy()

class Speech(Highlight, BaseContent):
    """ Speech
    """
    security = ClassSecurityInfo()

    # This name appears in the 'add' box
    archetype_name = 'Speech'

    meta_type = 'Speech'
    portal_type = 'Speech'
    allowed_content_types = [] + list(getattr(
        Highlight, 'allowed_content_types', []))
    filter_content_types = 0
    global_allow = 1
    immediate_view = 'base_view'
    default_view = 'highlight_view'
    suppl_views = ()
    typeDescription = "Speech"
    typeDescMsgId = 'description_edit_speech'
    _at_rename_after_creation = True
    schema = Speech_schema
    content_icon = 'speech_icon.gif'

    security.declarePublic('getPublishDate')
    def getPublishDate(self):
        """ Publish date
        """
        return self.getEffectiveDate()

    security.declarePublic('setPublishDate')
    def setPublishDate(self, value, **kw):
        """ Set publish date
        """
        self.setEffectiveDate(value)

    # LinguaPlone doesn't check base classes for mutators
    security.declareProtected(ModifyPortalContent, 'setThemes')
    def setThemes(self, value, **kw):
        """ Use the tagging adapter to set the themes. """
        #value = filter(None, value)
        value = [val for val in value if val]
        tagging = IThemeTagging(self)
        tagging.tags = value


registerType(Speech, PROJECTNAME)
