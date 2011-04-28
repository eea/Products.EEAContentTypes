from zope.component.exceptions import ComponentLookupError
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.EEAContentTypes.interfaces import IRelations


def CountReferences(obj, portal, **kwargs):
    try:
        backreferences = IRelations(obj).backReferences()
        fwdreferences = IRelations(obj).forwardReferences()

        #TODO: temporary fix for "relatesToProducts" relation, see #2790
        if obj.portal_type in ['Data', 'EEAFigure']:
            backreferences.extend(IRelations(obj).backReferences(relatesTo='relatesToProducts'))
            fwdreferences.extend(obj.getRelatedProducts())

        return len(backreferences) + len(fwdreferences)
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

# countReferences index is made a callable
registerIndexableAttribute('countReferences', CountReferences)
