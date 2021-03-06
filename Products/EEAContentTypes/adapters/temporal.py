""" Adapters
"""
from zope.interface import implements

from .interfaces import ITemporalCoverageAdapter


def _get_field_value(obj, name):
    """ utility function to return value of field name
    """
    data = obj.getField(name)
    return data.getAccessor(obj)() if data else ()


class DefaultTemporalCoverageAdapter(object):
    """ Basic temporalCoverage Adapter that looks for the value found within
        the field
    """
    implements(ITemporalCoverageAdapter)

    def __init__(self, context):
        self.context = context

    def value(self):
        """ Returns temporalCoverage Field value
        """
        return _get_field_value(self.context, 'temporalCoverage')


class EventsTemporalCoverageAdapter(object):
    """ Events temporalCoverage Adapter which constructs the value from the
        start and end date
    """
    implements(ITemporalCoverageAdapter)

    def __init__(self, context):
        self.context = context

    def value(self):
        """ Events temporalCoverage constructed from the start and end date
        """
        obj = self.context
        # construct the index value from the start and end date
        start_date = obj.getField('startDate').getAccessor(obj)() or None
        start_year = []
        end_year = []
        if start_date:
            start_year.append(start_date.year())
        end_date = obj.getField('endDate').getAccessor(obj)() or None
        if end_date:
            end_year.append(end_date.year())
        if start_year or end_year:
            start_year.extend(end_year)
            coverage = set(start_year)
            if coverage:
                return tuple(coverage)
        else:
            return ()
