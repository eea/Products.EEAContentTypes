""" Tests
"""

from doctest import DocFileSuite
import doctest
import unittest

from zope.component.testing import setUp, tearDown


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
