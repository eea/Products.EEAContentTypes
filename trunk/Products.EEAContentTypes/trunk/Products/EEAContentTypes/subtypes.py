""" Subtypes
"""
from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import ISchema
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from eea.themecentre.content.ThemeTaggable import ThemesField
from eea.indicators.content.interfaces import IExternalDataSpec
from eea.geotags import field
from eea.geotags import widget
from p4a.subtyper.engine import Subtyper as BaseSubtyper, DescriptorWithName
from p4a.subtyper.interfaces import (
    IPossibleDescriptors,
    IPortalTypedPossibleDescriptors
)
from p4a.video.subtype import TopicVideoContainerDescriptor as \
        BaseTopicVideoContainerDescriptor, _
from zope.component import adapts
from zope.component import queryAdapter
from zope.interface import Interface, implements
from Products.LinguaPlone.public import StringField
from Products.LinguaPlone.public import InAndOutWidget


class ExtensionStringField(ExtensionField, StringField):
    """ derivative of stringfield for extending schemas """

class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """

class ExtensionGeotagsMultifield(ExtensionField, field.GeotagsLinesField):
    """ derivative of blobfield for extending schemas """

class ExtensionThemesField(ExtensionField, ThemesField):
    """ derivative of themesfield for extending schemas """

class LocationSchemaExtender(object):
    """ Extends base schema with extra fields.
    To be used for base content class. """
    implements(ISchemaExtender)

    fields =  [
            ExtensionGeotagsMultifield(
                name='location',
                schemata='categorization',
                widget=widget.GeotagsWidget(
                    label='Geotags / Locations',
                    description=('Geotags: multiple geographical locations '
                                 'related to this content. Click Edit button '
                                 'to select a location')
                    )
                )
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        #TODO Refactor location for Organisation and Event #4788
        if getattr(self.context, 'portal_type', None) in (
            'Organisation', 'QuickEvent'):
            # No schema extender
            return []
        return self.fields


class QuickEventSchemaModifier(object):
    """ Extends base schema with extra fields.
    To be used for base content class. """

    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        schema['location'].schemata = 'default'
        schema['themes'].schemata = 'default'


class ThemesSchemaExtender(object):
    """ Extends schema with themes field
    """
    implements(ISchemaExtender)

    fields = [
        ExtensionThemesField(
            name='themes',
            schemata='categorization',
            validators=('maxValues',),
            widget=InAndOutWidget(
                maxValues=3,
                label="Themes",
                description="Choose max 3 themes",
                ),
            languageIndependent=True,
            vocabulary_factory=u"Allowed themes for edit",
        ),
    ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        """ Fields
        """
        return self.fields

class RequiredSchemaModifier(object):
    """ Modify schema
    """
    implements(ISchemaModifier)

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """ Modify schema
        """
        portal_type = getattr(self.context, 'portal_type', '')

        #TODO Move this to zcml
        if portal_type not in [
            'Article', 'Highlight', 'PressRelease', 'Speech',
            'DiversityReport', 'Data', 'EEAFigure', 'EcoTip',
            'EyewitnessStory', 'GIS Application', 'Document',
            'PolicyDocumentReference', 'Report', 'SOERKeyFact',
            'SOERMessage', 'File']:
            return

        if 'subject' in schema:
            schema['subject'].required = True
        if 'location' in schema:
            schema['location'].required = True

        if 'themes' in schema:
            if not IExternalDataSpec.providedBy(self.context):
                schema['themes'].required = True

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
    """Interface for editing single location"""
    geotag = widget.location.GeotagSingleField(
            title = u"Geotag",
            description=(u"Geotag: a single geographical location for "
                         "this content.")
            )


class GeotagSingleEdit(GeotagMixinEdit):
    """ Single edit
    """
    implements(IGeotagSingleEdit)


class IGeotagMultiEdit(Interface):
    """Interface for editing multiple locations"""

    geotag = widget.location.GeotagMultiField(
            title = u"Geotags",
            description=(u"Geotags: multiple geographical locations related to"
                         " this content.")
            )


class GeotagMultiEdit(GeotagMixinEdit):
    """ Multi Edit
    """
    implements(IGeotagMultiEdit)


class Subtyper(BaseSubtyper):
    """We override the default subtyper because of broken logic in its
    possible_types implementation. The default implementation, due to
    adapter resolution order, doesn't take into account adapters for
    IPortalTypedPossibleDescriptors

    Also, not it's possible to hide the menu for content types where
    it doesn't make sense. This is due to the fact that the subtyper
    in p4a.video is registered for somewhat generic interfaces
    (for ex: IATFolder)
    """
    _skip = ('Data', 'EEAFigure')

    def possible_types(self, obj):
        """ Possible types
        """
        if obj.portal_type in self._skip:
            return []

        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)


class TopicVideoContainerDescriptor(BaseTopicVideoContainerDescriptor):
    """ Topic container
    """
    title = _("Video Topic Container")
