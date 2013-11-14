""" Catalog
"""
from Products.Archetypes.interfaces import IBaseContent, IBaseObject
from Products.EEAContentTypes.interfaces import IRelations, IEEAPossibleContent
from Products.EEAContentTypes.interfaces import IEEAContent

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


