from zope.component.exceptions import ComponentLookupError
from Products.CMFPlone.CatalogTool import registerIndexableAttribute
from Products.EEAContentTypes.interfaces import IRelations


def CountReferences(object, portal, **kwargs):
    try:
        backreferences = IRelations(object).backReferences()
        fwdreferences = IRelations(object).forwardReferences()

        #TODO: temporary fix for "relatesToProducts" relation, see #2790
        if object.portal_type in ['Data', 'EEAFigure']:
            backreferences.extend(IRelations(object).backReferences(relatesTo='relatesToProducts'))
            fwdreferences.extend(object.getRelatedProducts())

        return len(backreferences) + len(fwdreferences)
    except (ComponentLookupError, TypeError, ValueError):
        # The catalog expects AttributeErrors when a value can't be found
        raise AttributeError

# countReferences index is made a callable
registerIndexableAttribute('countReferences', CountReferences)
