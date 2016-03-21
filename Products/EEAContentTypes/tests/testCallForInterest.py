""" Tests
"""

from DateTime import DateTime

from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase


class testCallForInterest(EEAContentTypeTestCase):
    """
        Test-cases for class(es) CallForInterest
    """

    def test_CallForInterest_with_invoke_id_not_change(self):
        """
            Test id not change with only invoke
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='CallForInterest', id="ci",
                                 title='Call For Interest',
                                 openDate=DateTime(),
                                 closeDate=DateTime(),
                                 applicationDate=DateTime())

        cft = getattr(root, cid)
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.id, "ci")

    def test_CallForInterest_with_invoke_title_not_change(self):
        """
            Teste title not change with only invoke
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='CallForInterest', id="ci",
                                 title='Call For Interest',
                                 openDate=DateTime(),
                                 closeDate=DateTime(),
                                 applicationDate=DateTime())

        cft = getattr(root, cid)
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.title, "Call For Interest")

    def test_CallForInterest_with_processForm_id_change(self):
        """
            Test id change after call processForm because
            _rename_after_creation=True
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='CallForInterest', id="ci")

        cft = getattr(root, cid)
        cft.processForm(data=1, metadata=1,
                        values={'title': "Call For Interest",
                                'openDate': DateTime(),
                                'closeDate': DateTime(),
                                'applicationDate': DateTime()})
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.id, "call-for-interest")
        self.assertEqual(cft.title, "Call For Interest")

    def test_CallForInterest_with_processForm_title_not_change(self):
        """
            Test title not change after processForm
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='CallForInterest', id="ci")

        cft = getattr(root, cid)
        cft.processForm(data=1, metadata=1,
                        values={'title': "Call For Interest",
                                'openDate': DateTime(),
                                'closeDate': DateTime(),
                                'applicationDate': DateTime()})
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.title, "Call For Interest")


def test_suite():
    """ Tests suite
    """
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testCallForInterest))
    return suite
