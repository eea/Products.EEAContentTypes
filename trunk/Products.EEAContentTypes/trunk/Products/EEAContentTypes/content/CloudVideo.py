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
    TextField, TextAreaWidget, registerType, AnnotationStorage
)
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
schema = Schema((
    ImageField('Image',
        required=False,
          languageIndependent=True,
          storage = AnnotationStorage(migrate=True),
        widget=ImageWidget(
            label='Image',
            label_msgid='EEAContentTypes_label_image',
            description_msgid='EEAContentTypes_help_image',
            i18n_domain='EEAContentTypes'
        )
    ),

    TextField(
                name='cloudUrl',
                languageIndependent=True,
                required = True,
                storage = AnnotationStorage(migrate=True),
                default_content_type = 'text/html',
                allowable_content_types =('text/html',),
                default_output_type = 'text/html',
                widget = TextAreaWidget(
                    description = 'The embedding code for the video from' \
                                    ' some external sites eg. Vimeo or Youtube',
                    label = "Cloud Url"
                )
        ),

),
)

CloudVideo_schema = (getattr(ATFile, 'schema', Schema(())).copy() +
                    ThemeTaggable_schema.copy() +
                    schema.copy())

finalizeATCTSchema(CloudVideo_schema, folderish=False, moveDiscussion=False)
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
    #content_icon               = 'FlashFile.gif'
    immediate_view             = 'file_view'
    default_view               = 'file_view'
    suppl_views                = ()
    typeDescription            = "CloudVideo"
    typeDescMsgId              = 'description_edit_cloudvideo'

    schema = CloudVideo_schema


registerType(CloudVideo, PROJECTNAME)
