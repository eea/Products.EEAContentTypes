""" Subtypes
"""
import logging

from datetime import datetime
from AccessControl import ClassSecurityInfo
from plone.registry.interfaces import IRegistry
from plone.app.blob.field import ImageField
from plone.app.blob.subtypes.blob import SchemaExtender as BlobSchemaExtender
from plone.app.blob.subtypes.file import SchemaExtender as FileSchemaExtender
from plone.app.blob.subtypes.image import SchemaExtender as ImageSchemaExtender
from zope.i18nmessageid import MessageFactory
from zope.interface import Interface, implements
from zope.component import adapts
from zope.component import getUtility


from Products.validation import V_REQUIRED
from Products.Archetypes.Widget import MultiSelectionWidget
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import ISchema
from Products.Archetypes.atapi import StringField, StringWidget
from Products.ATContentTypes.configuration import zconf
from Products.EEAContentTypes.browser.interfaces import \
    IEEAContentRegistryRequiredFields
from Products.EEAContentTypes.utils import \
    excluded_temporal_coverage_schemaextender_tuple
from Products.LinguaPlone.public import InAndOutWidget
from Products.LinguaPlone.public import ImageWidget
from Products.LinguaPlone.public import LinesField
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender

from eea.dataservice.content.schema import ManagementPlanField
from eea.dataservice.content.schema import ManagementPlanWidget
from eea.forms.browser.app.temporal_coverage import grouped_coverage
from eea.geotags import field
from eea.geotags import widget
from eea.relations.component import getBackwardRelationWith
from eea.relations.component import getForwardRelationWith
from eea.relations.field import EEAReferenceField
from eea.relations.interfaces import IAutoRelations
from eea.relations.widget import EEAReferenceBrowserWidget
from eea.themecentre.content.ThemeTaggable import ThemesField
from eea.design.browser.interfaces import IEEACommonLayer


_ = MessageFactory('Products.EEAContentTypes')


logger = logging.getLogger('EEAContentTypes')


class ExtensionRelationsField(ExtensionField, EEAReferenceField):
    """ derivative of relations for extending schemas """


class ExtensionStringField(ExtensionField, StringField):
    """ derivative of stringfield for extending schemas """


class ExtensionImageField(ExtensionField, ImageField):
    """ derivative of imagefield for extending schemas """


class ExtensionLinesField(ExtensionField, LinesField):
    """ derivative of linesfield for extending schemas """

    security = ClassSecurityInfo()

    security.declarePrivate('set')

    def set(self, instance, value, **kwargs):
        """ Expands year range input into a list of all elements
        """
        expanded_range = []

        for elem in value:
            if "-" in elem and elem != "-1":
                start, end = elem.split("-")
                expanded_range.extend(range(int(start), int(end) + 1))
            else:
                expanded_range.append(int(elem))

        save_value = [str(x) for x in set(expanded_range)]

        superclass = super(ExtensionLinesField, self)
        superclass.set(instance, save_value, **kwargs)


class TemporalMultiSelectionWidget(MultiSelectionWidget):
    """ derivative of MultiSelectionWidget in order to
        add a new formatting function
    """

    def formatted_value(self, value):
        """ Format value from temporal widget
        """
        try:
            return "\n".join(grouped_coverage(value))
        except ValueError:
            return "\n".join(value)


class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """


class ExtensionGeotagsMultifield(ExtensionField, field.GeotagsLinesField):
    """ derivative of blobfield for extending schemas """


class ExtensionThemesField(ExtensionField, ThemesField):
    """ derivative of themesfield for extending schemas """


class ExtensionManagementField(ExtensionField, ManagementPlanField):
    """ derivative of themesfield for extending schemas """


class RelationsSchemaExtender(object):
    """ Extends relations filed
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    fields = (
        ExtensionRelationsField('relatedItems',
                                schemata='categorization',
                                relationship='relatesTo',
                                multiValued=True,
                                languageIndependent=True,
                                keepReferencesOnCopy=True,
                                widget=EEAReferenceBrowserWidget(
                                    label='Related items',
                                    description='Specify relations to other '
                                                'content within Plone.'
                                )
                                ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Returns relatedItems field
        """
        # List of content types where relatedItems field
        # is override in specific schemata
        if self.context.portal_type in (
                "DavizVisualization", "Specification", "Assessment",
                "AssessmentPart", "QuickEvent", "Report", "IndicatorFactSheet",
                "Storytelling"):
            return []

        # Due to #4705 base_view shows related widget which should be
        # rendered by the macro from main_template
        if self.context.portal_type in ("Promotion",):
            self.fields[0].widget.visible['view'] = 'invisible'

        return self.fields


class LocationSchemaExtender(object):
    """ Extends base schema with extra fields.
        To be used for base content class.
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    multiple_location = (
        ExtensionGeotagsMultifield(
            name='location',
            schemata='categorization',
            required=False,
            languageIndependent=True,
            widget=widget.GeotagsWidget(
                label='Geotags / Locations',
                description=('Geotags: multiple geographical locations '
                             'related to this content. Click Edit button '
                             'to select a location')
            )
        ),
    )

    single_location = (
        ExtensionGeotagsSinglefield(
            name='location',
            schemata='categorization',
            required=False,
            languageIndependent=True,
            widget=widget.GeotagsWidget(
                label='Geographic coverage',
                description=(
                    'Type in here the exact geographic names/places '
                    'that are covered by the data. Add Countries names only '
                    'if the data displayed is really about the entire country.'
                    ' Example of locations/places are lakes, rivers, cities, '
                    'marine areas, glaciers, bioregions like alpine '
                    'region etc.')
            )
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """

        # Organisation has the previous location widget on default
        if getattr(self.context, 'portal_type', None) == 'Organisation':
            self.multiple_location[0].schemata = 'default'
            self.multiple_location[0].widget.label = "Organisation Address"
            self.multiple_location[0].widget.label_msgid = \
                "dataservice_label_address"
            self.multiple_location[0].widget.description = (
                'Geographical location '
                'related to this Organisation. Click Edit button'
                ' to select a location')
            self.multiple_location[0].widget.description_msgid = \
                "dataservice_help_address"
        elif self.context.portal_type in ('Data', "Assessment",
                                          "AssessmentPart"):
            # remove location schema extender for Data, see #9423
            # remove also for Assessment see 22232
            return ()
        else:
            self.multiple_location[0].schemata = 'categorization'
            self.multiple_location[0].widget.label = "Geographic coverage"
            self.multiple_location[0].widget.description = (
                'Geographic coverage describes the locations/places covered'
                ' by the content item.')
        return self.multiple_location


class ThemesSchemaExtender(object):
    """ Extends schema with themes field
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    fields = (
        ExtensionThemesField(
            name='themes',
            schemata='categorization',
            validators=('maxValues',),
            required=False,
            widget=InAndOutWidget(
                maxValues=5,
                label="Themes",
                description="Choose max 5 themes",
            ),
            languageIndependent=True,
            vocabulary_factory=u"Allowed themes for edit",
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        if getattr(self.context, 'portal_type', None) in ('QuickEvent',):
            # No schema extender for QuickEvent
            return []
        return self.fields


class TemporalCoverageSchemaExtender(object):
    """ Extends schema with temporalCoverage field
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    fields = (
        ExtensionLinesField(
            name='temporalCoverage',
            languageIndependent=True,
            schemata='categorization',
            required=False,
            multiValued=1,
            widget=TemporalMultiSelectionWidget(
                macro="temporal_widget",
                helper_js=("temporal_widget.js",),
                size=15,
                label="Temporal coverage",
                description=("The temporal scope of the content of the data "
                             "resource. Temporal coverage will typically "
                             "include a set of years or time ranges."),
                label_msgid='dataservice_label_coverage',
                description_msgid='dataservice_help_coverage',
                i18n_domain='eea',
            )
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        portal_type = getattr(self.context, 'portal_type', False)
        excluded_types = excluded_temporal_coverage_schemaextender_tuple() or \
            []
        if portal_type in excluded_types:
            # No schema extender for these content types as they already have
            # the temporalCoverage field though normal schema
            return []
        return self.fields


class ManagementPlanFieldExtender(object):
    """ Extends schema with eeaManagementPlan field
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    fields = (
        ExtensionManagementField(
            name='eeaManagementPlan',
            languageIndependent=True,
            schemata='categorization',
            required=True,
            default=(datetime.now().year, ''),
            validators=('management_plan_code_validator',),
            vocabulary_factory=u"Temporal coverage",
            widget=ManagementPlanWidget(
                format="select",
                label="EEA Management Plan",
                description=_("EEA Management plan code."),
                label_msgid='dataservice_label_eea_mp',
                description_msgid='dataservice_help_eea_mp',
                i18n_domain='eea',
            )
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        return self.fields


class RequiredSchemaModifier(object):
    """ Modify schema
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """

        getCanonical = getattr(self.context, 'getCanonical', None)
        if getCanonical:
            try:
                canonical = getCanonical()
            except Exception, err:
                logger.debug(err)
            else:
                if self.context != canonical:
                    # Language independent doesn't work with required property
                    return
        registry = getUtility(IRegistry)
        records = registry.records
        reg_name = IEEAContentRegistryRequiredFields.__identifier__
        # required way to get the values that start with the name of the
        # interface as seen in the doctests of plone.registry
        values = records.values(reg_name + ".", reg_name + "0")
        for value in values:
            name = value.field.title
            ctypes = value.value
            if self.context.portal_type in ctypes:
                if name in schema:
                    xfield = schema[name].copy()
                    xfield.required = True
                    schema[name] = xfield


class DocumentImageSchemaExtender(object):
    """ Extends image field
    """

    implements(ISchemaExtender, IBrowserLayerAwareExtender)

    layer = IEEACommonLayer

    _fields = (
        ExtensionImageField(name="image",
                            schemata="default",
                            widget=ImageWidget(
                                label=_("Image"),
                                description=_("Image used for cover, "
                                              "thumbnail and listings."
                                              "Size and image width should be"
                                              " of minimum 1920px")),
                            i18n_domain='plone',
                            languageIndependent=True,
                            allowable_content_types=('image/gif', 'image/jpeg',
                                                     'image/jpg', 'image/png',
                                                     'image/tiff'),
                            pil_quality=zconf.pil_config.quality,
                            pil_resize_algo=zconf.pil_config.resize_algo,
                            max_size=(7000, 7000),
                            sizes=None,
                            validators=(
                                ('isNonEmptyFile', V_REQUIRED),
                                ('imageMinSize', V_REQUIRED),
                                ('checkFileMaxSize', V_REQUIRED),
                            )
                            ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Returns image field
        """
        if self.context.portal_type == "Document":
            return self._fields
        return []


class LanguageIndependentModifier(object):
    """ Modify schema to remove languageIndependent flag
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        lfield = 'effectiveDate'
        if lfield in schema:
            xfield = schema[lfield].copy()
            xfield.languageIndependent = False
            schema[lfield] = xfield


class DavizRequirementsSchemaModifier(object):
    """ Modify schema
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        # 30066 temporalCoverage and location are required_for_published
        fields = ['temporalCoverage', 'location']
        for dfield in fields:
            if dfield in schema:
                xfield = schema[dfield].copy()
                xfield.required_for_published = True
                schema[dfield] = xfield


class StorytellingRequirementsSchemaModifier(object):
    """ Modify schema for Storytelling content type
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        fields = ['temporalCoverage', 'location', 'themes', 'relatedItems', 'subject']
        for dfield in fields:
            if dfield in schema:
                xfield = schema[dfield].copy()
                xfield.required_for_published = True
                xfield.required = True
                schema[dfield] = xfield


class DashboardRequirementsSchemaModifier(object):
    """ Modify schema for Dashboard content type
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        # #72857 temporalCoverage, themed and location are required
        fields = ['temporalCoverage', 'location', 'themes']
        for dfield in fields:
            if dfield in schema:
                xfield = schema[dfield].copy()
                xfield.required_for_published = True
                xfield.required = True
                schema[dfield] = xfield


class KeywordsSchemaModifier(object):
    """ Fix keywords postback bug http://dev.plone.org/ticket/12334
    """
    implements(ISchemaModifier, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Fields
        """
        if 'subject' in schema:
            # since only subject has the keywordsWidget macro we can disable
            # giving it eea_keywords since eea.tags as it's own keywords macro
            # schema['subject'].widget.macro = 'eea_keywords'
            # TODO: this fix doesn't apply to this problem anymore,
            # to be removed or to be replaced if a keywordsWidget field is
            # added

            # make subject field languageIndependent as required since ticket
            # 8761
            schema['subject'].languageIndependent = True


class GeotagMixinEdit(object):
    """ Edit
    """
    adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    @property
    def geotag(self):
        """ Getter
        """
        schema = ISchema(self.context)
        xfield = schema['location']
        accessor = xfield.getAccessor(self.context)
        return accessor()

    @geotag.setter
    def geotag(self, value):
        """ Setter
        """
        schema = ISchema(self.context)
        xfield = schema['location']
        mutator = xfield.getMutator(self.context)
        mutator(value)


class IGeotagSingleEdit(Interface):
    """ Interface for editing single location
    """
    geotag = widget.location.GeotagSingleField(
        title=u"Geotag",
        description=(u"Geotag: a single geographical location for "
                     "this content.")
    )


class GeotagSingleEdit(GeotagMixinEdit):
    """ Single edit
    """
    implements(IGeotagSingleEdit)


class IGeotagMultiEdit(Interface):
    """ Interface for editing multiple locations
    """
    geotag = widget.location.GeotagMultiField(
        title=u"Geotags",
        description=(u"Geotags: multiple geographical locations related to"
                     " this content.")
    )


class GeotagMultiEdit(GeotagMixinEdit):
    """ Multi Edit
    """
    implements(IGeotagMultiEdit)


class GetCanonicalRelations(object):
    """ Reproduce the relations of the canonical object,
        In our case, the canonicals should all be in EN.
    """

    implements(IAutoRelations)

    def __init__(self, context):
        self.context = context

    def __call__(self, **kwargs):
        tabs = {}
        if not getattr(self.context, 'isCanonical', None):
            return tabs.items()
        if self.context.isCanonical():
            # Canonical object, we return nothing
            return []
        else:
            lang = self.context.Language()
            canonical = self.context.getCanonical()
            # Get canonical relations forward and backward.
            # As translations are related to the canonical object,
            # we specify the parameters in the backward not to list them.

            # Used in relations/browser/app/macro.py, but doesn't work
            # when there are no relations on the object
            #
            # fieldname = kwargs.get('fieldname', 'relatedItems')
            # field = canonical.getField(fieldname)
            # if field:
            #    accessor = field.getAccessor(self.context)
            #    rel_forwards = accessor()
            rel_forwards = canonical.getRefs(kwargs.get('relation',
                                                        'relatesTo'))
            if rel_forwards:
                # Get translations of forward relations, if
                # translations don't exist, return canonical

                contentTypes = {}
                nonForwardRelations = set()
                for relation in rel_forwards:
                    # Get the relation type name
                    if not relation:
                        continue
                    portalType = relation.portal_type
                    if portalType in nonForwardRelations:
                        nonForwardRelations.add(portalType)
                        continue
                    if portalType not in contentTypes:
                        forward = getForwardRelationWith(self.context, relation)
                        if not forward:
                            continue
                        name = forward.getField('forward_label').getAccessor(
                            forward)()
                        contentTypes[portalType] = name
                        tabs[name] = []
                    name = contentTypes[portalType]
                    # #14831 check if relations isn't already added since you
                    # could receive a bunch of translations of a single object
                    # which would result in duplication of relations
                    context_relation = relation.getTranslation(lang)
                    tab = tabs[name]
                    if context_relation:
                        if context_relation not in tab:
                            tab.append(context_relation)
                    else:
                        if relation not in tab:
                            tab.append(relation)

            rel_backwards = canonical.getBRefs(kwargs.get('relation',
                                                          'relatesTo'))
            if rel_backwards:
                # Get translations of backward relations, if
                # translations don't exist, return canonical
                contentTypes = {}
                nonBackwardRelations = set()
                for relation in rel_backwards:
                    if not relation:
                        continue
                    portalType = relation.portal_type
                    if portalType in nonBackwardRelations:
                        nonBackwardRelations.add(portalType)
                        continue
                    if portalType not in contentTypes:
                        backward = getBackwardRelationWith(self.context,
                                                           relation)
                        if not backward:
                            continue
                        name = backward.getField('backward_label').getAccessor(
                            backward)()
                        contentTypes[portalType] = name
                        tabs[name] = []
                    name = contentTypes[portalType]

                    context_relation = relation.getTranslation(lang)
                    tab = tabs[name]
                    if context_relation:
                        if context_relation not in tab:
                            tab.append(context_relation)
                    else:
                        if relation not in tab:
                            tab.append(relation)

            if tabs:
                return tabs.items()
            else:
                return []


class ExcludeTOCSchemaExtender(object):
    """ Extends schema with exclude field
    """
    implements(ISchemaExtender, IBrowserLayerAwareExtender)
    layer = IEEACommonLayer

    fields = (
        ExtensionStringField(
            name='tocExclude',
            schemata='settings',
            required=False,
            widget=StringWidget(
                label="Exclude from Table of Contents",
                description="Type id of what do you want to exclude.",
            ),
            languageIndependent=True,
        ),
    )

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        return self.fields


class EEABlobSchemaExtender(BlobSchemaExtender):
    """ Custom Blob Schema Extender
    """
    def getFields(self):
        """ Schema Fields
        """
        self.fields[0].searchable = False
        return self.fields


class EEAFileSchemaExtender(FileSchemaExtender):
    """ Custom File Schema Extender
    """
    def getFields(self):
        """ Schema Fields
        """
        self.fields[0].searchable = False
        return self.fields


class EEAImageSchemaExtender(ImageSchemaExtender):
    """ AT Image Schema extender
    """
    def getFields(self):
        """ Schema Fields
        """
        self.fields[0].allowable_content_types = (
            'image/gif', 'image/jpeg',
            'image/png', 'image/svg+xml'
        )
        return self.fields
