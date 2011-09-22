from Products.Archetypes.interfaces import IBaseContent
from Products.Archetypes.interfaces import ISchema
from archetypes.schemaextender.field import ExtensionField
from archetypes.schemaextender.interfaces import ISchemaExtender
from eea.geotags import field
from eea.geotags import widget
from p4a.subtyper.engine import Subtyper as BaseSubtyper, DescriptorWithName
from p4a.subtyper.interfaces import IPossibleDescriptors, IPortalTypedPossibleDescriptors
from zope.component import adapts
from zope.component import queryAdapter
from zope.interface import Interface, implements

class ExtensionGeotagsSinglefield(ExtensionField, field.GeotagsStringField):
    """ derivative of blobfield for extending schemas """


class ExtensionGeotagsMultifield(ExtensionField, field.GeotagsLinesField):
    """ derivative of blobfield for extending schemas """


class BaseContentSchemaExtender(object):
    implements(ISchemaExtender)
#    adapts(IVideoEnhanced)
    adapts(IBaseContent)

    fields =  [
            ExtensionGeotagsSinglefield(
                name='location',
                schemata='categorization',
                default='',
                widget=widget.GeotagsWidget(
                    label='Location',
                    description='Single geographical location'
                    )
                )
            ]

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields


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
    """Interface for edit single location"""
    geotag = widget.location.GeotagSingleField(
            title = u"Geotag",
            description=u"The location of the video"
            )


class GeotagSingleEdit(GeotagMixinEdit):
    implements(IGeotagSingleEdit)


class IGeotagMultiEdit(Interface):
    """Interface for edit multiple locations"""

    geotag = widget.location.GeotagMultiField(
            title = u"Geotag",
            description=u"The locations of the video"
            )


class GeotagMultiEdit(GeotagMixinEdit):
    implements(IGeotagMultiEdit)


class Subtyper(BaseSubtyper):
    """We override the default subtyper because of broken logic in its
    possible_types implementation. The default implementation, due to
    adapter resolution order, doesn't take into account adapters for
    IPortalTypedPossibleDescriptors
    """

    def possible_types(self, obj):
        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)

