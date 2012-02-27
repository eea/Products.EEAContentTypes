""" FlashFile """
from plone.app.blob.field import  ImageField
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.file import ATFile
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import ICloudVideo
from Products.EEAContentTypes.content.ThemeTaggable import (
    ThemeTaggable,
    ThemeTaggable_schema,
)
from Products.Archetypes.atapi import (
    Schema, ImageWidget, 
    registerType, AnnotationStorage
)

schema = Schema((
        ImageField('Image',
            required=False,
              languageIndependent=True,
            widget=ImageWidget(
                label='Image',
                label_msgid='EEAContentTypes_label_image',
                description_msgid='EEAContentTypes_help_image',
                i18n_domain='EEAContentTypes'
            )
        ),
    ),
)

CloudVideo_schema = (getattr(ATFile, 'schema', Schema(())).copy() +
                    ThemeTaggable_schema.copy() +
                    schema.copy())

CloudVideo_schema['file'].required = False


class CloudVideo(ATFile, ThemeTaggable):
    """ CloudVideo contenttype
    """
    security = ClassSecurityInfo()
    implements(ICloudVideo)

    # This name appears in the 'add' box
    archetype_name             = 'CloudVideo'
    meta_type                  = 'CloudVideo'
    portal_type                = 'CloudVideo'
    allowed_content_types      = [] + list(getattr(ATFile,
                                                   'allowed_content_types', []))
    filter_content_types       = 0
    global_allow               = 1
    allow_discussion           = 0
    immediate_view             = 'file_view'
    default_view               = 'file_view'
    suppl_views                = ()
    typeDescription            = "CloudVideo"
    typeDescMsgId              = 'description_edit_cloudvideo'

    schema = CloudVideo_schema

registerType(CloudVideo, PROJECTNAME)
