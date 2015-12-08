""" Evolve 85 profile
"""
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility

from Products.EEAContentTypes.browser.interfaces import \
    IEEAContentRegistryRequiredFields, IEEAContentTypesSettings


def evolve(context):
    """ Update the registry with the latest required fields """

    registry = queryUtility(IRegistry)
    required_fields = registry.forInterface(IEEAContentRegistryRequiredFields,
                                            check=False)
    required_fields.temporalCoverage = ('Infographic', 'Data', 'EEAFigure')
    types_settings = registry.forInterface(IEEAContentTypesSettings,
                                           check=False)
    types_settings.noTemporalCoverageSubtyperFor = (
        'Assessment', 'IndicatorFactSheet', 'Link')
