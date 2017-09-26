""" CountryRegionSection Content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes import public, DisplayList
from Products.Archetypes.Widget import SelectionWidget, ImageWidget
from Products.Archetypes.atapi import Schema, registerType, LinesField, \
    LinesWidget, TextField, RichWidget, StringField
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import ICountryRegionSection
from plone.app.blob.field import ImageField
from zope.interface import implements
from Products.validation import V_REQUIRED


schema = Schema((

    TextField(
        name='body',
        searchable=True,
        required_for_published=False,
        required=False,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label="Body Text",
            description="Body text used for the country/region intro page",
            label_msgid='EEAContentTypes_label_body',
            i18n_domain='eea',
        ),
    ),
    ImageField('image',
               required=True,
               storage=public.AnnotationStorage(migrate=True),
               languageIndependent=True,
               widget=ImageWidget(
                   label='Background image, use image with minimum width of '
                         '1920px',
                   label_msgid='EEAContentTypes_label_image',
                   description_msgid='EEAContentTypes_help_image',
                   i18n_domain='eea',
                   show_content_type=False),
               validators=(
                   ('imageMinSize', V_REQUIRED),
               )
               ),

    LinesField(
        name='externalLinks',
        languageIndependent=True,
        required=False,
        widget=LinesWidget(
            label="External links",
            description="External links, add one per line as: Title|url",
            label_msgid='EEAContentTypes_label_external_links',
            i18n_domain='eea',),
    ),
    StringField(
        name='type',
        required=True,
        widget=SelectionWidget(
            label="Item Type",
            format='select',
            default=['country'],
            description="Choose the types of object this portal type represents",
            label_msgid='EEAContentTypes_label_type',
            i18n_domain='eea'
        ),
        vocabulary="getSectionType",
    )
))

CountryRegion_schema = getattr(ATLink, 'schema', Schema(())).copy() + schema
CountryRegion_schema['remoteUrl'].searchable = False
CountryRegion_schema['remoteUrl'].required = False
CountryRegion_schema['remoteUrl'].widget.visible = {
    "edit": "invisible", "view": "visible"}


class CountryRegionSection(ATLink):
    """ CountryRegion contenttype
    """
    security = ClassSecurityInfo()
    schema = CountryRegion_schema
    implements(ICountryRegionSection)

    # This name appears in the 'add' box
    archetype_name = 'Country/Region section'
    portal_type = 'CountryRegionSection'

    immediate_view = 'link_view'
    default_view = 'link_view'
    meta_type = 'CountryRegionSection'
    allowed_content_types = []
    filter_content_types = 1
    global_allow = 1
    allow_discussion = 0
    suppl_views = ()
    typeDescription = "Country/Region section"
    typeDescMsgId = 'description_edit_country_region_section'

    _at_rename_after_creation = True

    def getRemoteUrl(self):
        """ remote url
        """
        sprops = self.portal_properties.site_properties
        fallback = 'https://eea.europa.eu/countries-and-regions/'
        app_url = sprops.getProperty('car_app_url', fallback)
        return app_url + self.id

    security.declarePublic('getVisibilityLevels')
    def getSectionType(self):
        """ Visibility levels
        """
        types = (('country', 'Country'),
                  ('region', 'Region'))
        return DisplayList(types)


registerType(CountryRegionSection, PROJECTNAME)
