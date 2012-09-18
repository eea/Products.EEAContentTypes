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
    registerType, TextField, TextAreaWidget
)

from Products.CMFCore.permissions import View

from Products.Archetypes.atapi import AnnotationStorage
from Products.LinguaPlone import public

from eea.forms.fields.ManagementPlanField import ManagementPlanField
from eea.forms.widgets.ManagementPlanWidget import ManagementPlanWidget
from datetime import datetime

schema = Schema((
        ImageField('image',
            required=False,
            storage = public.AnnotationStorage(migrate=True),
              languageIndependent=True,
            widget=ImageWidget(
                label='Image',
                label_msgid='EEAContentTypes_label_image',
                description_msgid='EEAContentTypes_help_image',
                i18n_domain='EEAContentTypes',
                show_content_type = False
            )
        ),
        TextField('cloudUrl', 
                languageIndependent=True,
                required = True,
                schemata = 'default',
                storage = AnnotationStorage(migrate=True),
                default_content_type = 'text/plain',
                validators = ('videoCloudUrlValidator',),
                allowable_content_types =('text/plain',),
                default_output_type = 'text/plain',
                widget = TextAreaWidget(
                    description = 'The embedding code for the video from' \
                                    ' external sites eg. Vimeo or Youtube',
                    label = "Cloud Url"
                )
        ), 
        ManagementPlanField(
            name='eeaManagementPlan',
            languageIndependent=True,
            required=True,
            default=(datetime.now().year, ''),
            validators = ('management_plan_code_validator',),

            vocabulary_factory="Temporal coverage",
            storage = AnnotationStorage(migrate=True),
            widget = ManagementPlanWidget(
                format="select",
                label="EEA Management Plan",
                description = ("EEA Management plan code."),
                label_msgid='dataservice_label_eea_mp',
                description_msgid='dataservice_help_eea_mp',
                i18n_domain='eea.dataservice',
                ),
            ),
    ),
)

CloudVideo_schema = (getattr(ATFile, 'schema', Schema(())).copy() +
                    ThemeTaggable_schema.copy() +
                    schema.copy())

# hide file field from CloudVideo
CloudVideo_schema['file'].required = False
CloudVideo_schema['file'].widget.visible = {"edit" : "invisible", "view":
                                                                "invisible"}


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

    security.declareProtected(View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """ Redirect to /view for CloudVideo to avoid file download 
        """
        return self.REQUEST.response.redirect(
                                        self.absolute_url() + "/view", 301)

    schema = CloudVideo_schema

registerType(CloudVideo, PROJECTNAME)
