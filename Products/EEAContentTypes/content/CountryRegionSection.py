""" CountryRegionSection Content type
"""
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content.link import ATLink
from Products.Archetypes import public, DisplayList
from Products.Archetypes.Widget import ImageWidget, SelectionWidget
from Products.Archetypes.atapi import Schema, registerType, LinesField, \
    LinesWidget, TextField, RichWidget, StringField
from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.interfaces import ICountryRegionSection
from plone.app.blob.field import ImageField
from zope.interface import implements


schema = Schema((

    TextField(
        name='body',
        searchable=True,
        required_for_published=True,
        required=True,
        allowable_content_types=('text/html',),
        default_content_type="text/html",
        default_output_type="text/x-html-safe",
        widget=RichWidget(
            label="Intro text",
            description="Intro text used for the country/region description",
            label_msgid='EEAContentTypes_label_body',
            i18n_domain='eea',
        ),
    ),
    ImageField('image',
               required=True,
               storage=public.AnnotationStorage(migrate=True),
               languageIndependent=True,
               widget=ImageWidget(
                   label='Background image',
                   label_msgid='EEAContentTypes_label_image',
                   description_msgid='EEAContentTypes_help_image',
                   i18n_domain='eea',
                   show_content_type=False)
               ),

    ImageField('flag',
               required=True,
               storage=public.AnnotationStorage(migrate=True),
               languageIndependent=True,
               widget=ImageWidget(
                   label='Flag image',
                   label_msgid='EEAContentTypes_label_flag',
                   description_msgid='EEAContentTypes_flag_image',
                   i18n_domain='eea',
                   show_content_type=False)
               ),
    LinesField(
        name='externalLinks',
        languageIndependent=True,
        required=False,
        widget=LinesWidget(
            label="External links",
            description=("External links for current country/region."),
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
CountryRegion_schema['subject'].required = True


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
        app_url = 'http://car.apps.eea.europa.eu/'
        return app_url + self.id

    security.declarePublic('getVisibilityLevels')
    def getSectionType(self):
        """ Visibility levels
        """
        types = (('country', 'Coutry'),
                  ('region', 'Region'))
        return DisplayList(types)


registerType(CountryRegionSection, PROJECTNAME)
