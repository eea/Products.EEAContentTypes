"""Plugins to modify @@rdf info
"""

from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.versions.interfaces import IVersionEnhanced
from eea.versions.versions import get_versions_api
from zope.component import adapts
from zope.interface import implements
import rdflib


class VersioningModifier(object):
    """Adds information about versioning
    """

    implements(ISurfResourceModifier)
    adapts(IVersionEnhanced)

    def __init__(self, context):
        self.context = context

    def run(self, rdf):
        """change the rdf resource
        """
        api = get_versions_api(self.context)

        rdf.dcterms_isReplacedBy = [rdflib.URIRef(i['url']) for
                                                        i in api.newest()]
        rdf.dcterms_replaces = [rdflib.URIRef(a['url']) for a in api.oldest()]

        rdf.save()
