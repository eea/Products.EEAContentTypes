"""Plugins to modify @@rdf info
"""

from Products.Archetypes.interfaces import IField
from eea.rdfmarshaller.archetypes.fields import ATField2Surf
from eea.rdfmarshaller.interfaces import ISurfResourceModifier
from eea.rdfmarshaller.interfaces import ISurfSession
from eea.versions.interfaces import IVersionEnhanced, IGetVersions
from zope.component import adapts
from zope.interface import implements, Interface
import rdflib
import surf


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
        api = IGetVersions(self.context)

        newer = api.later_versions()
        older = api.earlier_versions()
        resource.dcterms_isReplacedBy = [rdflib.URIRef(i['url']) for
                                                        i in newer]
        resource.dcterms_replaces = [rdflib.URIRef(a['url']) for a in older]

        resource.save()

        
class MediaField2Surf(ATField2Surf):
    """A mediafield to surf adapter for the "media" field
    """
    adapts(IField, Interface, ISurfSession)

    def value(self):
        """Tranform value to surf value
        """
        f = self.context.getMedia()
        if not len(f):
            return None

        return [rdflib.URIRef(f.absolute_url()+"/image_xlarge")]


class Provenances2Surf(ATField2Surf):
    """The provenances field
    """
    adapts(IField, Interface, ISurfSession)

    name = "wasDerivedFrom"
    prefix = "prov"

    def __init__(self, *args, **kwargs):
        super(Provenances2Surf, self).__init__(*args, **kwargs)
        surf.ns.register(prov="http://www.w3.org/ns/prov#")
        surf.ns.register(prv = "http://purl.org/net/provenance/ns#")
        store = self.session.get_default_store()
        store.reader.graph.bind('prov', surf.ns.PROV, override=True)
        store.reader.graph.bind('prv', surf.ns.PRV, override=True)
        store.reader.graph.bind('foaf', surf.ns.FOAF, override=True)
        store.reader.graph.bind('rdf', surf.ns.RDF, override=True)

    def value(self):
        """The adapted value for this field

        Desired output:

<prov:wasDerivedFrom> 
  <prv:DataItem> 
    <dcterms:title>Title of dataset</dcterms:title> 
    <foaf:isPrimaryTopicOf rdf:resource="http://organisation/urltodataset"/> 
    <prov:wasAttributedTo rdf:respurce="uri of owner"/> 
  </prv:DataItem> 
</prov:wasDerivedFrom>

        """
        DataItem = self.session.get_class(surf.ns.PRV.DataItem)

        output = []

        for i, prov in enumerate(self.field.getAccessor(self.context)()):
            #prov is {'owner': u'http://www.eea.europa.eu', 
            #         'link': u'http://www.eea.europa.eu/...', 
            #         'title': u'Corine Land Cover 2000 - 2006 changes'}

            d = DataItem(rdflib.BNode())
            d.dcterms_title = prov['title']
            d.foaf_isPrimaryTopicOf = rdflib.URIRef(prov['link'])
            d.prov_wasAttributedTo = rdflib.URIRef(prov['owner'])
            d.update()

            output.append(d)

        return output
