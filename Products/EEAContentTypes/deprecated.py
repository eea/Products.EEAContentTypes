"""
Deprecated functionality that will be removed in a later release of this
package
"""
from zope.component import queryAdapter
from p4a.subtyper.engine import Subtyper as BaseSubtyper, DescriptorWithName
from p4a.subtyper.interfaces import IPortalTypedPossibleDescriptors
from p4a.subtyper.interfaces import IPossibleDescriptors

class Subtyper(BaseSubtyper):
    """ We override the default subtyper because of broken logic in its
        possible_types implementation. The default implementation, due to
        adapter resolution order, doesn't take into account adapters for
        IPortalTypedPossibleDescriptors

        Also, not it's possible to hide the menu for content types where
        it doesn't make sense. This is due to the fact that the subtyper
        in p4a.video is registered for somewhat generic interfaces
        (for ex: IATFolder)
    """
    _skip = ('Data', 'EEAFigure')

    def possible_types(self, obj):
        """ Possible types
        """
        if obj.portal_type in self._skip:
            return []

        possible = queryAdapter(obj, IPortalTypedPossibleDescriptors)
        if possible and possible.possible:
            return (DescriptorWithName(n, c) for n, c in possible.possible)

        possible = IPossibleDescriptors(obj)
        return (DescriptorWithName(n, c) for n, c in possible.possible)

import warnings
warnings.warn("p4a.subtyper is deprecated. "
              "Please use marker interfaces instead",
              DeprecationWarning)
