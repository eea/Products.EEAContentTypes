""" Catalog
"""
from Products.Archetypes.interfaces import IBaseContent
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
