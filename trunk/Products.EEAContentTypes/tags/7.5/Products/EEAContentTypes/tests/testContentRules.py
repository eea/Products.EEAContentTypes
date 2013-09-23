from Products.EEAContentTypes.contentrules.actions import (
    EnableDisableDiscussionAction, EnableDisableDiscussionEditForm)
from plone.app.contentrules.rule import Rule
from plone.app.contentrules.tests.base import ContentRulesTestCase
from plone.contentrules.engine.interfaces import IRuleStorage
from plone.contentrules.rule.interfaces import IExecutable
from plone.contentrules.rule.interfaces import IRuleAction
from zope.component import getUtility, getMultiAdapter
from zope.component.interfaces import IObjectEvent
from zope.interface import implements


class DummyEvent(object):
    implements(IObjectEvent)

    def __init__(self, object):
        self.object = object


class TestEnableDisableDiscussionRule(ContentRulesTestCase):

    def _element(self):
        return getUtility(IRuleAction, 
            name='Products.EEAContentTypes.actions.enable_disable_discussion')

    def afterSetUp(self):
        self.setRoles(('Manager', ))
        self.folder.invokeFactory('Document', 'd1')

    def testRegistered(self):
        element = self._element()
        self.assertEquals(
            'Products.EEAContentTypes.actions.EnableDisableDiscussion', 
            element.addview)
        self.assertEquals('edit', element.editview)
        self.assertEquals(None, element.for_)

    def testInvokeAddView(self):
        element = self._element()
        storage = getUtility(IRuleStorage)
        storage[u'foo'] = Rule()
        rule = self.portal.restrictedTraverse('++rule++foo')

        adding = getMultiAdapter((rule, self.portal.REQUEST), name='+action')
        addview = getMultiAdapter((adding, self.portal.REQUEST), 
                                   name=element.addview)

        addview.createAndAdd(data={'action': 'enabled', })

        e = rule.actions[0]
        self.failUnless(isinstance(e, EnableDisableDiscussionAction))
        self.assertEquals('enabled', e.action)

    def testInvokeEditView(self):
        element = self._element()
        e = EnableDisableDiscussionAction()
        editview = getMultiAdapter((e, self.folder.REQUEST), 
                                    name=element.editview)
        self.failUnless(isinstance(editview, EnableDisableDiscussionEditForm))

    def testExecute(self):
        e = EnableDisableDiscussionAction()
        e.action = 'enabled'

        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), 
                              IExecutable)
        self.assertEquals(True, ex())

        self.assertEquals(True, self.folder.d1.isDiscussable())

    def testExecuteWithError(self):
        e = EnableDisableDiscussionAction()
        e.action = 'foo'

        old_state = self.folder.d1.isDiscussable()
        ex = getMultiAdapter((self.folder, e, DummyEvent(self.folder.d1)), 
                             IExecutable)
        self.assertEquals(False, ex())

        self.assertEquals(old_state, self.folder.d1.isDiscussable())


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestEnableDisableDiscussionRule))
    return suite
