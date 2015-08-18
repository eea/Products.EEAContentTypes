""" Workflow tests
"""
import hmac
import time
from hashlib import sha1 as sha
from Acquisition import aq_base

from Products.CMFPlone.tests.utils import MockMailHost
from Products.MailHost.interfaces import IMailHost
from plone.keyring.interfaces import IKeyManager
from plone.protect.authenticator import _getUserName
from zope.component import getUtility, getSiteManager

from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase


class TestWorkflow(EEAContentTypeTestCase):
    """ Test-cases for class(es) workflow. """

    def afterSetUp(self):
        """ Set up
        """
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        self.workflow = self.portal.portal_workflow
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])

        self.folder.invokeFactory('Document', id='doc')
        self.setRoles('Manager')
        self.workflow.doActionFor(self.folder.doc, 'publish')
        self.historyMarker = \
            '<span class="historyaction state-publish">publish</span>'

    def beforeTearDown(self):
        """ Tear down
        """
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def testAnonymous(self):
        """ Test as Anonymous
        """
        self.logout()
        res = self.folder.doc.workflow_action_message(
            type='document', editUrl='url').lower().find(self.historyMarker)
        self.assertEquals(res, -1)
        res1 = self.folder.doc.workflow_confirmation_message(
            type='document').lower().find(self.historyMarker)
        self.assertEquals(res1, -1)

    def testManager(self):
        """ Test as Manager
        """
        self.login('manager')
        res = self.folder.doc.workflow_action_message(
            type='document', editUrl='url').lower().find(self.historyMarker)
        self.failIf(res == -1)
        res1 = self.folder.doc.workflow_confirmation_message(
            type='document').lower().find(self.historyMarker)
        self.failIf(res1 == -1)


class TestWorkflowModified(EEAContentTypeTestCase):
    """ Test that object.modified() updates on state change
    """
    _ptypes = set()

    def beforeTearDown(self):
        """ Tear down
        """
        self.portal.MailHost = self.portal._original_MailHost
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(aq_base(self.portal._original_MailHost),
                           provided=IMailHost)

    def afterSetUp(self):
        """ Set up """
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = mailhost = MockMailHost('MailHost')
        sm = getSiteManager(context=self.portal)
        sm.unregisterUtility(provided=IMailHost)
        sm.registerUtility(mailhost, provided=IMailHost)

        self.workflow = self.portal.portal_workflow
        self.portal.acl_users._doAddUser('manager', 'secret', ['Manager'], [])
        self.setRoles('Manager')

        if not hasattr(self.folder, 'sandbox'):
            self.folder.invokeFactory('Folder', 'sandbox')
        self.sandbox = self.folder['sandbox']

        children = list(self.ptypes)
        self.sandbox.setConstrainTypesMode(1)
        self.sandbox.setImmediatelyAddableTypes(children)
        self.sandbox.setLocallyAllowedTypes(children)

        ptypes = self.portal.portal_types
        for ptype in children:
            ptypes[ptype].global_allow = True

        for ptype in self.ptypes:
            try:
                self.sandbox.invokeFactory(ptype, id=ptype, title=ptype)
            except Exception:
                continue

    @property
    def ptypes(self):
        """ Return all EEA Content-Types, filtered
        """
        if self._ptypes:
            return self._ptypes

        putils = self.portal.plone_utils
        for ptype in putils.getUserFriendlyTypes():
            if 'Vdex' in ptype:
                continue
            elif 'Vocabulary' in ptype:
                continue
            elif 'Criterion' in ptype:
                continue
            elif 'Cache' in ptype:
                continue
            elif 'EEAFigureFile' in ptype:
                # This ctype depends on parent. Skip it
                continue
            elif ptype == 'Assessment':
                # This ctype depends on parent. Skip it
                continue
            self._ptypes.add(ptype)

        return self._ptypes

    def test_publish(self):
        """ Test state changed to published
        """
        self.login('manager')

        # Before state change modification dates
        objects = self.sandbox.objectValues()
        before = [doc.modified() for doc in objects]

        # Sleep for a second
        time.sleep(1)

        for doc in objects:
            doc.content_status_modify(
                workflow_action='publish', comment='Published by test')

        # After state change modification dates
        after = [doc.modified() for doc in objects]

        errors = set()
        children = objects
        for index, date in enumerate(before):
            did = children[index].getId()
            # If date is unchanged after state change,
            # add doc id to errors
            if date == after[index]:
                errors.add(did)

        # Fail if errors
        self.failIf(errors, errors)

    def test_publish_effective_date(self):
        """ Test that effective date is set when objects are published
        """
        self.login('manager')

        objects = self.sandbox.objectValues()
        # Before state change modification dates
        before = []

        # Sleep for a second
        time.sleep(1)
        modified_objects = []
        skipped_objects = set()
        one_workflow_or_none_objects = set()
        for doc in objects:
            review_state = self.workflow.getInfoFor(doc, 'review_state', None)
            # one_state_workflow has the published state as the default and
            # only review state
            if not review_state or review_state == 'published':
                one_workflow_or_none_objects.add(doc)
                continue
            current_effective_date = doc.effective()
            doc.content_status_modify(
                workflow_action='publish', comment='Published by test')
            # used by data_workflow
            doc.content_status_modify(
                workflow_action='quickPublish', comment='Published by test')

            if self.workflow.getInfoFor(doc, 'review_state', None) == \
                    'published':
                before.append(current_effective_date)
                modified_objects.append(doc)
            else:
                skipped_objects.add(doc)
        # After state change modification dates
        after = [doc.effective() for doc in modified_objects]

        errors = set()
        children = modified_objects
        for index, date in enumerate(before):
            did = children[index].getId()
            # If date is unchanged after state change,
            # add doc id to errors
            if date == after[index]:
                errors.add(did)

        print "\n TESTED Objects: \n"
        for obj in modified_objects:
            print obj.portal_type

        print "\n SKIPPED ONE STATE AND NO WORKFLOW Objects: \n"
        for obj in one_workflow_or_none_objects:
            print obj.portal_type

        print "\n SKIPPED Objects: \n"
        for obj in skipped_objects:
            workflow = self.workflow.getWorkflowsFor(obj)
            workflow_title = workflow[0].title if workflow else "NO"
            print "%s --> %s workflow" % (obj.portal_type, workflow_title)

        # Fail if errors
        self.failIf(errors, errors)

        modified_objects_len = len(modified_objects)
        skipped_objects_len = len(skipped_objects)
        ratio = skipped_objects_len * 100 / modified_objects_len
        print "CURRENT SKIP RATIO %d" % ratio
        if ratio > 25:
            self.fail("More than 25% of the content types are skipped")

    def test_bulk_publish(self):
        """ Test bulk state changed to published
        """
        self.login('manager')
        objects = self.sandbox.objectValues()
        # Before state change modification dates
        before = [x.modified() for x in objects]

        # Sleep for a second
        time.sleep(1)

        paths = ['/'.join(y.getPhysicalPath())
                 for y in objects]


        # Publish

        manager = getUtility(IKeyManager)
        secret = manager.secret()
        user = _getUserName()

        hmac.new(secret, user, sha).hexdigest()

        # plone 4 form protection bypass
        self.setRequestMethod('POST')
        self.setupAuthenticator()

        self.sandbox.folder_publish(workflow_action='publish', paths=paths)

        # After state change modification dates
        after = [z.modified() for z in objects]

        errors = set()
        children = objects
        for index, date in enumerate(before):
            did = children[index].getId()

            # If date is unchanged after state change, add doc id to errors
            if date == after[index]:
                errors.add(did)

        # Fail if errors
        self.failIf(errors, errors)


def test_suite():
    """ Suite
    """
    import unittest

    return unittest.TestSuite(
        tests=(
            unittest.makeSuite(TestWorkflow),
            unittest.makeSuite(TestWorkflowModified),
        ))
