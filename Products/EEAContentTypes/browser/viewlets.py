""" Custom viewlets
"""
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter
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
        plone = getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')
        return plone.is_view_template() and \
               _available(self,
                          excluded_geographical_coverage_content_types) and \
                getattr(self.context, 'location', False)


class TemporalCoverageViewlet(common.ViewletBase):
    """ TemporalCoverage field Viewlet
    """
    render = ViewPageTemplateFile('zpt/viewlets/temporal_coverage.pt')

    @property
    def available(self):
        """ Condition for rendering of this viewlets
        """
        plone = getMultiAdapter((self.context, self.request),
                                name=u'plone_context_state')
        return plone.is_view_template() and \
               _available(self, excluded_temporal_coverage_content_types)


class ExcludeTOCViewlet(common.ViewletBase):
    """ ExcludeCoverage field Viewlet
    """
    render = ViewPageTemplateFile('zpt/viewlets/tocExclude_coverage.pt')

    @property
    def available(self):
        """ Condition for rendering of this viewlets
        """
        # import pdb; pdb.set_trace()
        if not getattr(self.context, 'tableContents', False):
            return False
        return getattr(self.context, 'tocExclude', False)

    @property
    def exclude(self):
     """ Get excluded toc
     """
     # import pdb; pdb.set_trace()
     field = getattr(self.context, 'getField', lambda name: None)("tocExclude")
     if not field:
         return ""
     accessor = getattr(field, 'getAccessor',  lambda name: None)(self.context)
     if not accessor:
         return ""
     return accessor()
