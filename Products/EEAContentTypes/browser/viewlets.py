""" Custom viewlets
"""
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets import common
from Products.EEAContentTypes.utils import \
    excluded_geographical_coverage_content_types, \
    excluded_temporal_coverage_content_types


def _available(self, method):
    """ Helper method
    """
    ptype = getattr(self.context, 'portal_type')
    if ptype:
        return True if ptype not in method() else False
    return False


class GeographicalCoverageViewlet(common.ViewletBase):
    """ GeographicalCoverage field Viewlet
    """
    render = ViewPageTemplateFile('zpt/viewlets/geographical_coverage.pt')

    @property
    def available(self):
        """ Condition for rendering of this viewlets
        """
        return _available(self, excluded_geographical_coverage_content_types)


class TemporalCoverageViewlet(common.ViewletBase):
    """ TemporalCoverage field Viewlet
    """
    render = ViewPageTemplateFile('zpt/viewlets/temporal_coverage.pt')

    @property
    def available(self):
        """ Condition for rendering of this viewlets
        """
        return _available(self, excluded_temporal_coverage_content_types)
