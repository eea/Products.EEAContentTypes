""" Tests
"""

from DateTime import DateTime
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase


class testNegotiatedProcedure(EEAContentTypeTestCase):
    """
        Test-cases for class(es) NegotiatedProcedure
    """

    def test_NegotiatedProcedure_with_invoke_id_not_change(self):
        """
            Test id not change with only invoke
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='NegotiatedProcedure', id="np",
                                 title='Negociated Procedure',
                                 openDate=DateTime(),
                                 closeDate=DateTime(),
                                 applicationDate=DateTime())

        cft = getattr(root, cid)
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.id, "np")

    def test_NegotiatedProcedure_with_invoke_title_not_change(self):
        """
            Teste title not change with only invoke
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='NegotiatedProcedure', id="np",
                                 title='Negociated Procedure',
                                 openDate=DateTime(),
                                 closeDate=DateTime(),
                                 applicationDate=DateTime())

        cft = getattr(root, cid)
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.title, "Negociated Procedure")

    def test_NegotiatedProcedure_with_processForm_id_change(self):
        """
            Test id change after call processForm because
            _rename_after_creation=True
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='NegotiatedProcedure', id="np")

        cft = getattr(root, cid)
        cft.processForm(data=1, metadata=1,
                        values={'title': "Negociated Procedure",
                                'openDate': DateTime(),
                                'closeDate': DateTime(),
                                'applicationDate': DateTime()})
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.id, "negociated-procedure")
        self.assertEqual(cft.title, "Negociated Procedure")

    def test_NegotiatedProcedure_with_processForm_title_not_change(self):
        """
            Test title not change after processForm
        """
        self.setRoles('Manager')
        root = self.folder
        workflowTool = root.portal_workflow

        cid = root.invokeFactory(type_name='NegotiatedProcedure', id="np")

        cft = getattr(root, cid)
        cft.processForm(data=1, metadata=1,
                        values={'title': "Negociated Procedure",
                                'openDate': DateTime(),
                                'closeDate': DateTime(),
                                'applicationDate': DateTime()})
        workflowTool.doActionFor(cft, "open")

        self.assertEqual(cft.title, "Negociated Procedure")


def test_suite():
    """ Tests suite
    """
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testNegotiatedProcedure))
    return suite
