""" Tests
"""

from doctest import DocFileSuite
from zope.component.testing import setUp, tearDown
import doctest
import unittest


def test_suite():
    """ Suite
    """
    flags = (doctest.ELLIPSIS |
             doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    return unittest.TestSuite((
        DocFileSuite('normalizer.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=flags),
        ))
