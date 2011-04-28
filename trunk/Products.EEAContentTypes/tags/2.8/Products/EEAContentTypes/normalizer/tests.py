import unittest

from zope.component.testing import setUp, tearDown
from zope.testing import doctest
from zope.testing.doctestunit import DocFileSuite

def configurationSetUp(self):
    setUp()

def test_suite():
    flags = (doctest.ELLIPSIS |
             doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    return unittest.TestSuite((
        DocFileSuite('normalizer.txt',
                     setUp=configurationSetUp,
                     tearDown=tearDown,
                     optionflags=flags),
        ))
