from Products.EEAContentTypes.interfaces import IRelations
from plone.indexer.decorator import indexer


@indexer
def CountReferences(obj):
    try:
        backreferences = IRelations(obj).backReferences()
        fwdreferences = IRelations(obj).forwardReferences()

        #TODO: temporary fix for "relatesToProducts" relation, see #2790
        if obj.portal_type in ['Data', 'EEAFigure']:
            backreferences.extend(IRelations(obj).backReferences(relatesTo='relatesToProducts'))
            fwdreferences.extend(obj.getRelatedProducts())

        return len(backreferences) + len(fwdreferences)
    except (TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

