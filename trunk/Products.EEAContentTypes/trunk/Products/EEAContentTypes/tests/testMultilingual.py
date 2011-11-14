""" Test multilinguality
"""
from Products.Five import zcml
import Products.EEAContentTypes
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase

class TestMultilingual(EEAContentTypeTestCase):
    """Test cases for LinguaPlone and multilingual features."""

    def afterSetUp(self):
        """ Set up
        """
        zcml.load_config('configure.zcml', Products.EEAContentTypes)

    def test_smartFolderCriteria(self):
        """ Smart folder criteria
        """
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Topic', id='topic')
        crit = self.folder.topic.addCriterion('Creator',
                                              'ATSimpleStringCriterion')
        crit.setValue('dummyuser')

        # translate the smart folder and check if it has the criteria
        # that was added to the original smart folder
        self.folder.topic.addTranslation('sv')
        svcrit = self.folder['topic-sv'][
            'crit__Creator_ATSimpleStringCriterion']
        self.assertEqual(svcrit.Value(), 'dummyuser')


def test_suite():
    """ Suite
    """
    from unittest import TestSuite, makeSuite
    suite = makeSuite(TestMultilingual)

    from Products.PloneTestCase import layer
    from Products.PloneTestCase import setup

    if setup.USELAYER:
        if not hasattr(suite, 'layer'):
            suite.layer = layer.PloneSite

    return  TestSuite(suite)
