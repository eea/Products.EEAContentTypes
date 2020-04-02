""" Dashboard Content type
"""
from AccessControl import ClassSecurityInfo
from plone.app.blob.field import ImageField
from Products.Archetypes.atapi import (AnnotationStorage, ImageWidget,
                                       RichWidget, Schema, TextAreaWidget,
                                       TextField, registerType)
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.link import ATLink
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IInteractiveDashboard
from Products.validation import V_REQUIRED
from zope.interface import implements


schema = Schema((
    TextField(
        name='introduction',
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label="Introduction",
            description="Introduction of GIS Map Application",
            label_msgid='EEAContentTypes_label_introduction',
            i18n_domain='eea',
        ),
    ),
    TextField(
        name='embed',
        languageIndependent=True,
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=TextAreaWidget(
            label="Embed code",
            description=("Tableau embed code should be pasted here."),
            label_msgid='EEAContentTypes_label_embed',
            i18n_domain='eea',),
        ),

    ImageField('image',
               required=False,
               languageIndependent=True,
               storage=AnnotationStorage(migrate=True),
               swallowResizeExceptions= \
                   zconf.swallowImageResizeExceptions.enable,
               pil_quality=zconf.pil_config.quality,
               pil_resize_algo=zconf.pil_config.resize_algo,
               max_size=zconf.ATImage.max_image_dimension,
               sizes={'large': (768, 768),
                      'preview': (400, 400),
                      'mini': (200, 200),
                      'thumb': (128, 128),
                      'tile': (64, 64),
                      'icon': (32, 32),
                      'listing': (16, 16),
                      },
               validators=(('isNonEmptyFile', V_REQUIRED),
                           ('imageMinSize', V_REQUIRED)),
               widget=ImageWidget(
                   description='High-res preview image'
                               ' (at least FHD 1920x1080)',
                   label='Preview image',
                   show_content_type=False, )
               ),

    TextField(
        name='body',
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label="More information",
            description=("Description of methodology "
                         "and calculations behind this."),
            label_msgid='EEAContentTypes_label_body',
            i18n_domain='eea',
            ),
        ),
))

DASHBOARD_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema
DASHBOARD_schema['description'].required = True
DASHBOARD_schema['remoteUrl'].required = False
DASHBOARD_schema['remoteUrl'].widget.visible = {
    "edit": "invisible", "view": "invisible"}
DASHBOARD_schema['subject'].required = True


class Dashboard(ATLink):
    """ Dashboard contenttype
    """
    security = ClassSecurityInfo()
    schema = DASHBOARD_schema
    implements(IInteractiveDashboard)

    # This name appears in the 'add' box
    archetype_name = 'Dashboard (Tableau)'
    portal_type = 'Dashboard (Tableau)'

    meta_type = 'Dashboard'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'dashboard_view'
    default_view = 'dashboard_view'
    suppl_views = ()
    typeDescription = "Dashboard (Tableau)"
    typeDescMsgId = 'description_edit_dashboard'

    _at_rename_after_creation = True


registerType(Dashboard, PROJECTNAME)
