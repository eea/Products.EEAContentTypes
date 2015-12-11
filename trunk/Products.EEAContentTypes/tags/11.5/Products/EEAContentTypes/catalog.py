""" Catalog
"""
from Products.Archetypes.interfaces import IBaseContent, IBaseObject
from Products.ATContentTypes.interfaces.event import IATEvent
from plone.indexer.decorator import indexer

from Products.EEAContentTypes.interfaces import IRelations, IEEAPossibleContent
from .interfaces import ITemporalCoverageAdapter
from Products.EEAContentTypes.interfaces import IEEAContent
from eea.daviz.content.interfaces import IDavizVisualization


@indexer(IBaseContent)
def CountReferences(obj):
    """ Index number of references on objects
    """

    try:
        backreferences = IRelations(obj).backReferences()
        fwdreferences = IRelations(obj).forwardReferences()
        return len(backreferences) + len(fwdreferences)
    except (TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError


@indexer(IBaseObject)
def Subject(obj):
    """ Index subjects/keywords lowercase
    """
    try:
        data = obj.schema['subject'].getRaw(obj)
        data = tuple([x.lower() for x in data])

        # return results list without duplicates
        return tuple(set(data))
    except (TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError


@indexer(IEEAContent)
def GetTemporalCoverageForIEEAContent(obj):
    """ temporalCoverage indexer for IEEAContent types
    """
    if "portal_factory" in obj.absolute_url():
        raise AttributeError
    return ITemporalCoverageAdapter(obj).value()


@indexer(IEEAPossibleContent)
def GetTemporalCoverageForIEEAPossibleContent(obj):
    """ temporalCoverage indexer for IEEAPossibleContent types
    """
    if "portal_factory" in obj.absolute_url():
        raise AttributeError
    return ITemporalCoverageAdapter(obj).value()


@indexer(IATEvent)
def GetTemporalCoverageForIATEvent(obj):
    """ temporalCoverage indexer for IATEvent types such as our own QuickEvents
    """
    if "portal_factory" in obj.absolute_url():
        raise AttributeError
    return ITemporalCoverageAdapter(obj).value()


@indexer(IDavizVisualization)
def getDataOwnerForDaviz(obj):
    """ indexer for dataOwner get info from provenances field
    """
    data_owners = []

    try:
        field = obj.getField('provenances')
        provenances = field.getAccessor(obj)()
        for provenance in provenances:
            owner = provenance.get('owner', '')
            if owner not in data_owners:
                data_owners.append(owner)

        return data_owners
    except (TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError
