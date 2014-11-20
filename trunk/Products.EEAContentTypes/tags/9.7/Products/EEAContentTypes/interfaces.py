""" Interfaces
"""
from zope.interface import Interface, Attribute
from .adapters.interfaces import ITemporalCoverageAdapter

class IEEAPloneSite(Interface):
    """A marker interface for the EEA Plone site
    """


class ITransitionLogicalGuard(Interface):
    """ Transition logical guard
    """
    available = Attribute("boolean if transitions is available")


class ILocalRoleEmails(Interface):
    """ Local role emails
    """
    emails = Attribute("Dictionary with emails for each role")


class IRelations(Interface):
    """ An adapter that retrieves relations from any plone object. """

    def all(samePortalType=False):
        """ Gets all objects that are, in any way, related to this object. """

    def backReferences():
        """ Gets all objects that have references to this object. """

    def backReferencesWithSameType(self):
        """ Gets all objects that have references to this object,
        and are the same portal_type.
        """

    def forwardReferences():
        """ Gets all objects that this object has references to. """

    def autoContextReferences(portal_type=False):
        """ Gets all objects that are referenced from this objects
        back references.
        Can take portal_type parameter to designate the type of objects that
        the back references should search for
        """

    def byTheme(samePortalType=False, getBrains=False, constraints=False):
        """ Gets all objects that have the same theme tag is the adapted object.
           samePortalType argument should be true if the related objects should
           be of the same portal type as context. getBrains argument should be
           true if one only wants the brains back instead of the whole objects.
           This is mainly for performance.
        """

    def byPublicationGroup(samePortalType=True, getBrains=False):
        """ Get all objects that are the same type and same publication group.
        """

    def references():
        """" Gets both forward and backward references. """


class IRequiredFields(Interface):
    """ Marker interface for Content-Types that should have required metadata
        like: subject, location, themes
    """


class IEEAPossibleContent(Interface):
    """ Marker interface for posibil EEA Content-Types needed since some
        content types are created only with the xml types and they usually
        inherit the meta_type from the product that they are derrived from
    """


class IEEAContent(Interface):
    """ Marker interface for EEA Content-Types
    """

__all__ = [
    ITemporalCoverageAdapter.__name__
]
