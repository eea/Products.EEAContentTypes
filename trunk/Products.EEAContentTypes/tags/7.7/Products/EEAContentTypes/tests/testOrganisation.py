""" Tests for Organisation
"""
from App.Common import package_home
from Products.EEAContentTypes.browser.organisation import Organisation
from Products.EEAContentTypes.config import product_globals
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
import os


rdfFilename = os.path.join(
    package_home(product_globals), 'tests', 'eeastaff.rdf')


class testOrganisation(EEAContentTypeTestCase):
    """Test-cases for class(es) Organisation."""

    # from class Organisation:
    def test_getOrgData(self):
        """ Get Organisation data
        """
        rdf = open(rdfFilename, 'r')
        view = Organisation(rdf, self.app.REQUEST)
        result = [ res['orgname'] for res in view.getOrgData(org='IDS') ]
        answer = [ 'IDS1', 'IDS3' ]
        message = '%s != %s' % (result, answer)
        self.failIf( result != answer, message)

    # from class Organisation:
    def test_getManagers(self):
        """ Get managers
        """
        rdf = open(rdfFilename, 'r')
        view = Organisation(rdf, self.app.REQUEST)
        manager = view.getManager()
        result = manager['job_title']
        answer = 'Executive Director'
        message = '%s != %s' % (result, answer)
        self.failIf( result != answer, message)

def test_suite():
    """ Suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testOrganisation))
    return suite
