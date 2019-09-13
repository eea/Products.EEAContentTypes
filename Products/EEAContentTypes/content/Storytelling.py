""" Storytelling
"""
from AccessControl import ClassSecurityInfo
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content import document
from eea.themecentre.content.ThemeTaggable import ThemeTaggable
from Products.EEAContentTypes.content.interfaces import IStorytelling
from Products.EEAContentTypes.config import PROJECTNAME
from zope.interface import implements

SCHEMA = atapi.Schema((), )

STORYTELLING_schema = folder.ATFolderSchema.copy() + \
                      document.ATDocumentSchema.copy() + \
                      getattr(ThemeTaggable, 'schema', atapi.Schema(())).copy() + \
                      SCHEMA.copy()


class Storytelling(folder.ATFolder, document.ATDocumentBase, ThemeTaggable):
    """ Storytelling content type
    """
    security = ClassSecurityInfo()
    schema = STORYTELLING_schema
    implements(IStorytelling)
    meta_type = "Storytelling"
    portal_type = "Storytelling"
    archetypes_name = "Storytelling"

    #filter_content_types = 0
    #global_allow = 0
    #allow_discussion = 0
    #immediate_view = 'dashboard_view'
    #default_view = 'dashboard_view'
    #suppl_views = ()
    #typeDescription = "Dashboard (Tableau)"
    #typeDescMsgId = 'description_edit_dashboard'

    #_at_rename_after_creation = True

atapi.registerType(Storytelling, PROJECTNAME)