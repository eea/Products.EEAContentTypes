import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Products.EEAContentTypes.tests.EEAContentTypeTestCase import EEAContentTypeTestCase
from Products.EEAContentTypes.browser.frontpage import FrontpageCache
from DateTime import DateTime

class TestFrontpageCache(EEAContentTypeTestCase):

    def afterSetUp(self):
        self.catalog = self.portal.portal_catalog
        self.workflow = self.portal.portal_workflow

        # scripts sending email should not be run during tests
        self.workflow.frontpage_workflow.scripts._delObject('submitForWebQA')
        self.workflow.frontpage_workflow.transitions['submit'].after_script_name = None

        self.now = DateTime()
        self.setRoles('Manager')
        self.yesterday = self.now-1
        self.pressdate = self.now-3
        self.feeddate = self.now-2

        self.portal.portal_properties.frontpage_properties.promotionFolder = '/' + self.portal.getId() + '/promotions'
        self.portal.invokeFactory('Folder', id = 'promotions')
        self.portal.invokeFactory('Folder', id = 'rss')

        self.portal.promotions.invokeFactory('Promotion', id = 'prom_1',
            text = 'some text')
        obj = self.prom_1 = self.portal.promotions.prom_1
        self.workflow.doActionFor(obj, 'publish')

        self.portal.promotions.invokeFactory('Promotion', id = 'prom_2',
            text = 'some text')
        obj = self.prom_2 = self.portal.promotions.prom_2
        self.workflow.doActionFor(obj, 'publish')

        self.portal.invokeFactory('Highlight', id = 'high_1',
            text = 'some text')
        obj = self.high_1 = self.portal.high_1
        # add a 'publish' transition so we can go directly to published state
        stateDef = self.workflow.frontpage_workflow.states['new']
        stateDef.setProperties(title="""New""",
                               transitions=['submit', 'publish'])
        self.workflow.doActionFor(obj, 'publish')

        self.portal.invokeFactory('PressRelease', id = 'press_1',
            text = 'some text')
        obj = self.press_1 = self.portal.press_1
        self.workflow.doActionFor(obj, 'submit')
        self.workflow.doActionFor(obj, 'publish')

        self.portal.rss.invokeFactory('RSSFeedRecipe', id = 'feed_1',
            text = 'some text')
        obj = self.feed_1 = self.portal.rss.feed_1
        self.workflow.doActionFor(obj, 'publish')

        self.portal.rss.invokeFactory('RSSFeedRecipe', id = 'feed_2',
            text = 'some text')
        obj = self.feed_2 = self.portal.rss.feed_2
        self.workflow.doActionFor(obj, 'publish')

    def test_modified_promotion(self):
        obj_dates = ((self.prom_1, self.now-22), (self.prom_2, self.yesterday),
                     (self.high_1, self.now-365), (self.press_1, self.now-2),
                     (self.feed_1, self.now-15), (self.feed_2, self.now-3))
        for obj, date in obj_dates:
            obj.setModificationDate(date)
            self.catalog.reindexObject(obj)

        view = FrontpageCache(self.portal, self.app.REQUEST)
        result = view.modified()
        message = '%s != %s' % (result, self.yesterday)
        self.failIf(result != self.yesterday, message)

    def test_modified_press(self):
        obj_dates = ((self.prom_1, self.now-22), (self.prom_2, self.now-4),
                     (self.high_1, self.now-365), (self.press_1, self.pressdate),
                     (self.feed_1, self.now-15), (self.feed_2, self.now-9))
        for obj, date in obj_dates:
            obj.setModificationDate(date)
            self.catalog.reindexObject(obj)

        view = FrontpageCache(self.portal, self.app.REQUEST)
        result = view.modified()
        message = '%s != %s' % (result, self.pressdate)
        self.failIf(result != self.pressdate, message)

    def test_modified_feed(self):
        obj_dates = ((self.prom_1, self.now-22), (self.prom_2, self.now-4),
                     (self.high_1, self.now-365), (self.press_1, self.now-9),
                     (self.feed_1, self.feeddate), (self.feed_2, self.now-5))
        for obj, date in obj_dates:
            obj.setModificationDate(date)
            self.catalog.reindexObject(obj)

        view = FrontpageCache(self.portal, self.app.REQUEST)
        result = view.modified()
        message = '%s != %s' % (result, self.feeddate)
        self.failIf(result != self.feeddate, message)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestFrontpageCache))
    return suite

if __name__ == '__main__':
    framework()
