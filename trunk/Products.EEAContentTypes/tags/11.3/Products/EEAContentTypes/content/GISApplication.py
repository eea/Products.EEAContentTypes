""" GisApplication Content type
"""
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import StringField
from Products.Archetypes.atapi import ImageWidget
from Products.Archetypes.atapi import Schema, registerType
from Products.validation import V_REQUIRED
from zope.interface import implements
from zope.event import notify

from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import IGISMapApplication
from Products.EEAContentTypes.events import GISMapApplicationWillBeRemovedEvent

schema = Schema((
    StringField(name="arcgis_url",
                widget=StringField._properties['widget'](
                    label="ArcGIS/EyeOnEarth url",
                    description='Enter the full web address ' \
                                'for Eye on Earth map, ArcGIS map etc...'
                ),
                required=False,
                schemata="default",
                validators=('isURL',),
                ),

    ImageField('image',
               required=True,
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
                               ' (at least 1024px width)',
                   label='Preview image',
                   show_content_type=False, )
               ),

))

GIS_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema

# Schema overwrites

GIS_schema['description'].required = True  # required to increase findability.
GIS_schema['remoteUrl'].required = False
GIS_schema['remoteUrl'].widget.label = 'Flash/Flex GIS application url'
GIS_schema['remoteUrl'].widget.description = \
    'Enter address to a flash/flex application usually ending with .swf'


class GISMapApplication(ATLink):
    """ GisApplication contenttype
    """
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
    suppl_views = ('gis_inline', 'gis_data_sources',)
    typeDescription = "GIS Map Application"
    typeDescMsgId = 'description_edit_gismapapplication'

    _at_rename_after_creation = True

    def getArcGisUID(self):
        """extract and return arcgis id from the arcgis url if exists otherwise
           return None.
        """
        idx = 0
        uid = None
        if hasattr(self, 'arcgis_url'):
            idx = self.arcgis_url.rfind('?webmap=')
        else:
            return None
        if idx > 0:
            uid = self.arcgis_url[idx + 8:]

        return uid

    def get_data_sources(self):
        """Extract relations  to types: "Data" or "ExternalDataSpec"
        (aka name is "Based on data" or "Based on external data")
        and format them a disctionary:
        <data source title/link> provided by <organisation name>
        """
        r = []
        relation_view = self.unrestrictedTraverse(
            '@@eea.relations.macro', None)
        if relation_view is not None:
            for relation in relation_view.forward():
                name = relation[0]
                #check the name is the desired one
                if name in ['Based on data', 'Based on external data']:
                    for item in relation[1]:
                        #process by portal_type
                        if item.portal_type == 'Data':
                            r.append({'url': '%s/' % item.absolute_url(),
                              'title': item.title,
                              'organisation': [(x, x) for x in item.dataOwner]
                            })
                        elif item.portal_tpye == 'ExternalDataSpec':
                            r.append({'url': '%s/' % item.absolute_url(),
                              'title': item.title,
                              'organisation': [(item.provider_name,
                                                item.provider_url)]
                            })
        return r

    def manage_beforeDelete(self, item, container):
        """Override manage_beforeDelete to be able to catch the
        proper backreferences. We could not use ObjectWillBeRemovedEvent
        because there's an override in Archetypes.Referenceble
        that will remove all relations and we need them
        """

        #only trigger event once, at the end, when dealing
        #with plone.app.linkintegrity
        if self.REQUEST.getURL().endswith('delete_confirmation'):
            #delete has been confirmed
            if self.REQUEST.form.get('_authenticator') and \
                not self.REQUEST.form.get('form.submitted'):
                notify(GISMapApplicationWillBeRemovedEvent(self))
        else:
            notify(GISMapApplicationWillBeRemovedEvent(self))

        super(GISMapApplication, self).manage_beforeDelete(item, container)

registerType(GISMapApplication, PROJECTNAME)
