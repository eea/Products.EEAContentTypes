""" Tests for Relations
"""
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from Products.EEAContentTypes.interfaces import IRelations
from eea.themecentre.interfaces import IThemeTagging
from zope.app.component.hooks import setSite

class TestRelations(EEAContentTypeTestCase):
    """ Test-cases for class(es) relations. """

    def afterSetUp(self):
        """ Set up
        """
        setSite(self.portal)
        self.setRoles('Member')
        self.workflow = self.portal.portal_workflow
        self.portal.acl_users._doAddUser(
            'reviewer', 'secret', ['Reviewer'], [])

        self.folder.invokeFactory('Document', id='unpub_air')
        self.folder.invokeFactory('Highlight', id='unpub_air_high')
        self.folder.invokeFactory('Promotion', id='unpub')
        self.folder.invokeFactory('Document', id='pub_air')
        self.folder.invokeFactory('PressRelease', id='priv_air_press')
        self.folder.invokeFactory('Document', id='pub')
        self.folder.invokeFactory('Document', id='rel_from')
        self.folder.invokeFactory('Document', id='rel_to')
        self.folder.invokeFactory('Document', id='rel_to2')
        self.folder.invokeFactory('Article', id='rel_not_same_type')
        self.folder.invokeFactory('Article', id='art1_pub')
        self.folder.invokeFactory('Article', id='art2_pub')
        self.folder.invokeFactory('Article', id='art3')

        IThemeTagging(self.folder.unpub_air).tags = ['air']
        IThemeTagging(self.folder.unpub_air_high).tags = ['air']
        IThemeTagging(self.folder.pub_air).tags = ['air']
        IThemeTagging(self.folder.priv_air_press).tags = ['air']

        self.folder.rel_from.setRelatedItems([self.folder.rel_to,
                                              self.folder.rel_to2,
                                              self.folder.rel_not_same_type,
                                              self.folder.unpub_air])
        self.folder.unpub_air.setRelatedItems([self.folder.rel_to])
        self.setRoles('Manager')

        self.workflow.doActionFor(self.folder.pub_air, 'publish')
        self.workflow.doActionFor(self.folder.pub, 'publish')
        self.workflow.doActionFor(self.folder.art1_pub, 'publish')
        self.workflow.doActionFor(self.folder.art2_pub, 'publish')

        air = self.portal.portal_vocabularies.themes.air
        self.workflow.doActionFor(air, 'publish')

        self.folder.unpub_air.reindexObject()
        self.folder.unpub_air_high.reindexObject()
        self.folder.unpub.reindexObject()
        self.folder.pub_air.reindexObject()
        self.folder.priv_air_press.reindexObject()
        self.folder.pub.reindexObject()

        # make all themes public (non deprecated)
        #for theme in self.portal.portal_vocabularies.themes.objectValues():
            #self.portal.portal_workflow.doActionFor(theme, 'publish')


    def testAnonymous(self):
        """ Anonymous
        """
        self.login('reviewer')
        related = IRelations(self.folder.pub_air).byTheme()
        ids = sorted([obj.getId() for obj in related])
        # we expect the objects with theme 'air' to be found
        self.assertEquals(ids, ['priv_air_press',
                                'unpub_air', 'unpub_air_high'])

        context = self.folder.pub_air
        related = IRelations(context).byTheme(portal_type=context.portal_type)
        ids = sorted(obj.getId() for obj in related)
        # we expect the Document objects with theme 'air' to be found
        self.assertEquals(ids, ['unpub_air'])

    def testAuthenticated(self):
        """ Authenitcated
        """
        self.login('test_user_1_')
        self.setRoles('Member')

        related = IRelations(self.folder.pub_air).byTheme()
        ids = sorted([obj.getId() for obj in related])
        # all objects that the user has permission to view should be
        # found, even private ones
        self.assertEquals(ids, ['priv_air_press',
                                'unpub_air', 'unpub_air_high'])

        constraint = {'review_state': 'published'}
        related = IRelations(self.folder.unpub_air).byTheme(
                constraints=constraint)
        ids = sorted(obj.getId() for obj in related)
        # all public objects that the user has permission to view should be
        # found
        self.assertEquals(ids, ['pub_air'])

    def testForwardReferences(self):
        """ Forward references
        """
        related = IRelations(self.folder.rel_from).forwardReferences()
        ids = sorted([obj.getId() for obj in related])
        self.assertEquals(ids, ['rel_not_same_type', 'rel_to',
                                'rel_to2', 'unpub_air'])

        related = IRelations(self.folder.rel_to).forwardReferences()
        ids = sorted(obj.getId() for obj in related)
        self.assertEquals(ids, [])

    def testAutoContext(self):
        """ Auto context
        """
        related = IRelations(self.folder.rel_to).autoContextReferences()
        ids = sorted([obj.getId() for obj in related])
        self.assertEquals(ids, ['rel_from', 'rel_not_same_type',
                                'rel_to2', 'unpub_air'])

        related = IRelations(self.folder.rel_to).autoContextReferences(
            portal_type=self.folder.rel_to.portal_type)
        ids = sorted(obj.getId() for obj in related)
        self.assertEquals(ids, ['rel_from', 'rel_to2', 'unpub_air'])

    def testBackReferences(self):
        """ Back references
        """
        related = IRelations(self.folder.rel_to).backReferences()
        ids = sorted([obj.getId() for obj in related])
        self.assertEquals(ids, ['rel_from', 'unpub_air'])

        related = IRelations(self.folder.rel_from).backReferences()
        ids = sorted(obj.getId() for obj in related)
        self.assertEquals(ids, [])

    def testAllRelations(self):
        """ All relations
        """
        constraint = {'review_state': 'published'}
        rels = IRelations(self.folder.unpub_air)
        related = rels.all(constraints=constraint)
        ids = sorted(obj.getId() for obj in related)
        self.assertEquals(ids, ['pub_air', 'rel_from', 'rel_to'])

    def testReferences(self):
        """ References
        """
        related = IRelations(self.folder.unpub_air).references()
        ids = sorted([obj.getId() for obj in related])
        self.assertEquals(ids, ['rel_from', 'rel_to'])

    def testPublicationGroup(self):
        """ Publication group
        """
        related = IRelations(self.folder.art1_pub).byPublicationGroup()
        ids = sorted([obj.getId() for obj in related])
        self.assertEquals(ids, ['art2_pub', 'art3', 'rel_not_same_type'])

        related = IRelations(self.folder.art2_pub).byPublicationGroup(
            constraints = {'review_state': 'published'})
        ids = sorted(obj.getId() for obj in related)
        self.assertEquals(ids, ['art1_pub'])

def test_suite():
    """ Suite
    """
    import unittest
    return  unittest.TestSuite(unittest.makeSuite(TestRelations))
