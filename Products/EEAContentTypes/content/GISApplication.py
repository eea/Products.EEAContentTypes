from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import Schema, registerType
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IGISMapApplication
from Products.validation import V_REQUIRED
from zope.interface import implements


schema = Schema((ImageField('image',
               required=True,
               languageIndependent=True,
               storage = AnnotationStorage(migrate=True),
               swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
               pil_quality = zconf.pil_config.quality,
               pil_resize_algo = zconf.pil_config.resize_algo,
               max_size = zconf.ATImage.max_image_dimension,
               sizes= {'large'   : (768, 768),
                       'preview' : (400, 400),
                       'mini'    : (200, 200),
                       'thumb'   : (128, 128),
                       'tile'    :  (64, 64),
                       'icon'    :  (32, 32),
                       'listing' :  (16, 16),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('imageMinSize', V_REQUIRED)),
               widget = ImageWidget(
                        description = 'High-res preview image'
                                      ' (at least 1024px width)',
                        label= 'Preview image',
                        show_content_type = False,)),

    ))

GIS_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema

#Schema overwrites
GIS_schema['remoteUrl'].widget.label = 'GIS application url'
GIS_schema['remoteUrl'].widget.description = 'Enter the full web address ' \
                       'for EEA Discomap, Eye on Earth map, ArcGIS map etc...'


class GISMapApplication(ATLink):
    security = ClassSecurityInfo()
    schema = GIS_schema
    implements(IGISMapApplication)

    # This name appears in the 'add' box
    archetype_name = 'GIS Application'
    portal_type = 'GIS Application'

    meta_type = 'GISMapApplication'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    allow_discussion = 0
    immediate_view = 'gis_view'
    default_view = 'gis_view'
    typeDescription = "GIS Map Application"
    typeDescMsgId = 'description_edit_gismapapplication'

    _at_rename_after_creation = True

registerType(GISMapApplication, PROJECTNAME)
