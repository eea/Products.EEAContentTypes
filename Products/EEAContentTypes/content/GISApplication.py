""" GisApplication Content type
"""
from AccessControl import ClassSecurityInfo

from Products.ATContentTypes.configuration import zconf
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes.atapi import AnnotationStorage
from Products.Archetypes.atapi import ImageField
from Products.Archetypes.atapi import StringField, TextField
from Products.Archetypes.atapi import ImageWidget, RichWidget
from Products.Archetypes.atapi import Schema, registerType
from Products.validation import V_REQUIRED
from zope.interface import implements
from zope.event import notify

from Products.CMFCore.utils import getToolByName

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

    TextField(
        name='body',
        allowable_content_types=('text/html',),
        widget=RichWidget(
            label="More information",
            description=("Description of methodology "
                         "and calculations behind this."),
            label_msgid='EEAContentTypes_label_body',
            i18n_domain='eea',
            ),
        default_content_type="text/html",
        searchable=True,
        default_output_type="text/x-html-safe",
        required_for_published=False,
        required=False,
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

    def getOrganisationName(self, url):
        """ Return the organisation name based on its URL """
        r = u''
        cat = getToolByName(self, 'portal_catalog')
        brains = cat.searchResults({'portal_type' : 'Organisation',
            'getUrl': url})
        if brains:
            r = brains[0].getObject().title
        return r

    def get_data_sources(self):
        """Extract relations  to types: "Data" or "ExternalDataSpec"
        and format them a disctionary:
        <data source title/link> provided by
        <organisation name> [and <organisation name>]
        """
        r = []
        for item in self.getRelatedItems():
            if item.portal_type == 'Data':
                organisations = []
                for url in item.dataOwner:
                    organisation = self.getOrganisationName(url)
                    if organisation:
                        organisations.append(organisation)
                r.append({'url': '%s/' % item.absolute_url(),
                  'title': item.title,
                  'organisations': organisations
                })
            elif item.portal_type == 'ExternalDataSpec':
                if item.provider_name:
                    organisation = item.provider_name
                else:
                    organisation = self.getOrganisationName(item.provider_url)
                r.append({'url': '%s/' % item.absolute_url(),
                  'title': item.title,
                  'organisations': [organisation]
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
