"""Plugins to modify @@rdf info
"""

from Products.Archetypes.interfaces import IField
from eea.geotags.storage.interfaces import IGeoTaggable 
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.versions.interfaces import IVersionEnhanced
from eea.versions.versions import get_versions_api
from zope.component import adapts
from zope.interface import implements, Interface
import rdflib

#from eea.geotags.interfaces import IGeoTags


class VersioningModifier(object):
    """Adds information about versioning
    """

    implements(ISurfResourceModifier)
    adapts(IVersionEnhanced)

    def __init__(self, context):
        self.context = context

    def run(self, resource, *args, **kwds):
        """change the rdf resource
        """
        api = get_versions_api(self.context)

        resource.dcterms_isReplacedBy = [rdflib.URIRef(i['url']) for
                                                        i in api.newest()]
        resource.dcterms_replaces = [rdflib.URIRef(a['url']) for a in api.oldest()]

        resource.save()

        
class MediaField2Surf(ATField2Surf):
    """A mediafield to surf adapter for the "media" field
    """
    adapts(IField, Interface, ISurfSession)

    def value(self):
        """Tranform value to surf value
        """
        return self.context.getMedia()

