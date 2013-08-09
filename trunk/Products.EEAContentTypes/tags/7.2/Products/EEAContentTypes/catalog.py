""" Catalog
"""
from Products.Archetypes.interfaces import IBaseContent, IBaseObject
from Products.EEAContentTypes.interfaces import IRelations
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
