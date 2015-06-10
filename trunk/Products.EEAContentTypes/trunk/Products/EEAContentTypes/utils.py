""" EEAContentTypes utility functions and classes
"""
from time import time

from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from Products.EEAContentTypes.browser.interfaces import IEEAContentTypesSettings


@ram.cache(lambda *args: time() // (60 * 60))
def excluded_geographical_coverage_content_types():
    """ Tuple of Contenttypes that should not display the geographicalCoverage
        viewlet cached for 1 hour
    """
    settings = eeacontenttypes_registry_settings()
    return getattr(settings, 'hideGeographicalCoverageFor', [])


@ram.cache(lambda *args: time() // (60 * 60))
def excluded_temporal_coverage_content_types():
    """ Tuple of Contenttypes that should not display the temporalCoverage
        viewlet cached for 1 hour
    """
    settings = eeacontenttypes_registry_settings()
    return getattr(settings, 'hideTemporalCoverageFor', [])


@ram.cache(lambda *args: time() // (60 * 60))
def excluded_temporal_coverage_schemaextender_tuple():
    """ Tuple of Contenttypes that should not display the temporalCoverage
        schemaextender field cached for 1 hour
    """
    settings = eeacontenttypes_registry_settings()
    return getattr(settings, 'noTemporalCoverageSubtyperFor', [])


def eeacontenttypes_registry_settings():
    """ Utility method returning the registry entry for IEEAContentTypesSettings
    """
    registry = getUtility(IRegistry)
    return registry.forInterface(IEEAContentTypesSettings, check=False)
