"""Plugins to modify @@rdf info
"""

from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.versions.interfaces import IVersionEnhanced
from eea.versions.versions import get_versions_api
from zope.component import adapts
from zope.interface import implements
from zope.component import getAdapter
from eea.geotags.interfaces import IGeoTags
from eea.geotags.storage.interfaces import IGeoTaggable 
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
        
        
class GeoTagRDFModifier(object):
    """Adds geotags information in rdf
    """

    implements(ISurfResourceModifier)
    adapts(IGeoTaggable)
    #adapts eea.geotags.storage.interfaces.IGeoTagged
    #or  eea.geotags.storage.interfaces.IGeoTaggable
    
    # points with geo positions
    #
    # xmlns:geo="http://www.w3.org/2003/01/geo/wgs84_pos#"
    # <geo:Point>
    #  <geo:lat>55.701</geo:lat>
    #  <geo:long>12.552</geo:long>
    # </geo:Point>
    #
    # 

    # Less precise: spatial coverage with DC terms
    # (using only literals can be missleading
    # because there are several places with same name)
    # 
    # <dct:spatial>Rome</dct:spatial>
    # 
    
    # Precise by pointing to geonames or other resources 
    # who have exact positions and definitions. we can use dc:subject
    #
    # <dct:subject rdf:resource="http://www.geonames.org/630671" />
    # or
    # <dct:subject rdf:resource="http://rdfdata.eionet.europa.eu/eea/biogeographic-regions/ALP" />
    #
    # or/and (but it looks like dct:spatial is defined to only have literals?)
    # <dct:spatial rdf:resource="http://www.geonames.org/630671" />
    #
    
    def __init__(self, context):
        self.context = context

    def run(self, rdf):
        """change the rdf resource
        """
        #import pdb; pdb.set_trace()
        #geo = getAdapter(self.context, IGeoTags)
        #rdf.dcterms_geotagtest = [rdflib.URIRef('http://rdfdata.eionet.europa.eu/page/ramon/nuts/RO')]
        #rdf.save()
