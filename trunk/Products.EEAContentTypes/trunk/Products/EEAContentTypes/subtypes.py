from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import ISchema
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from eea.geotags import field
from eea.geotags import widget
from p4a.subtyper.engine import Subtyper as BaseSubtyper, DescriptorWithName
from p4a.subtyper.interfaces import IPossibleDescriptors, IPortalTypedPossibleDescriptors
from p4a.video.subtype import TopicVideoContainerDescriptor as \
        BaseTopicVideoContainerDescriptor, _
from zope.component import adapts
from zope.component import queryAdapter
from zope.interface import Interface, implements


class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """


class ExtensionGeotagsMultifield(ExtensionField, field.GeotagsLinesField):
    """ derivative of blobfield for extending schemas """


class BaseContentSchemaExtender(object):
    """ Extends base schema with extra fields. 
    To be used for base content class. """
    implements(ISchemaExtender)

    fields =  [
            ExtensionGeotagsMultifield(
                name='location',
                schemata='categorization',
                widget=widget.GeotagsWidget(
                    label='Geotags / Locations',
                    description='Geotags: multiple geographical locations related to this content.'
                    )
                )
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

class RequiredFieldsExtender(BaseContentSchemaExtender):
    """ Extends the base schema and sets some fields required. 
    To be used for certain EEA content types."""
    def __init__(self, context):
        self.context = context
        self.fields[0].required = True
        
        
class GeotagMixinEdit(object):
    adapts(IBaseContent)

    def __init__(self, context):
        self.context = context

    def geotag():
        def get(self):
            schema = ISchema(self.context)
            field = schema['location']
            accessor = field.getAccessor(self.context)
            return accessor()

        def set(self, value):
            schema = ISchema(self.context)
            field = schema['location']
            mutator = field.getMutator(self.context)
            mutator(value)

        return property(get, set)

    geotag = geotag()


class IGeotagSingleEdit(Interface):
    """Interface for editing single location"""
    geotag = widget.location.GeotagSingleField(
            title = u"Geotag",
            description=u"Geotag: a single geographical location for this content."
            )


class GeotagSingleEdit(GeotagMixinEdit):
    implements(IGeotagSingleEdit)


class IGeotagMultiEdit(Interface):
    """Interface for editing multiple locations"""

    geotag = widget.location.GeotagMultiField(
            title = u"Geotags",
            description=u"Geotags: multiple geographical locations related to this content."
            )


class GeotagMultiEdit(GeotagMixinEdit):
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
        if obj.portal_type in self._skip:
            return []

        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)


class TopicVideoContainerDescriptor(BaseTopicVideoContainerDescriptor):
    title = _("Video Topic Container")

