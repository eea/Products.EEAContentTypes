""" Catalog
"""
from Products.Archetypes.interfaces import IBaseContent, IBaseObject
from Products.EEAContentTypes.interfaces import IRelations, IEEAPossibleContent
from Products.EEAContentTypes.interfaces import IEEAContent
from Products.ATContentTypes.interfaces.event import IATEvent

from plone.indexer.decorator import indexer

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


def _getFieldValue(obj, name):
    """ utility function to return value of field name
    """
    try:
        data = obj.getField(name)
        if data:
            return data.getAccessor(obj)()
        raise AttributeError
    except (TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError


@indexer(IEEAContent)
def GetTemporalCoverageForIEEAContent(obj):
    """ temporalCoverage indexer for IEEAContent types
    """
    return _getFieldValue(obj, 'temporalCoverage')


@indexer(IEEAPossibleContent)
def GetTemporalCoverageForIEEAPossibleContent(obj):
    """ temporalCoverage indexer for IEEAPossibleContent types
    """
    return _getFieldValue(obj, 'temporalCoverage')


@indexer(IATEvent)
def GetTemporalCoverageForIATEvent(obj):
    """ temporalCoverage indexer for IATEvent types
    """
    if "portal_factory" in obj.absolute_url():
        raise AttributeError

    # construct the index value from the start and end date
    start_date = obj.getField('startDate').getAccessor(obj)() or []
    start_year = []
    end_year = []
    if start_date:
        start_year.append(start_date.year())
    end_date = obj.getField('endDate').getAccessor(obj)() or []
    if end_date:
        end_year.append(end_date.year())
    if start_year or end_year:
        start_year.extend(end_year)
        coverage = set(start_year)
        if coverage:
            return tuple(coverage)
    else:
        raise AttributeError
