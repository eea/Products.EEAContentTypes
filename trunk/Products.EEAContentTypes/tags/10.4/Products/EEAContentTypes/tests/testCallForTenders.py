""" Tests
"""

from DateTime import DateTime

from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase


class testCallForTenders(EEAContentTypeTestCase):
    """Test-cases for class(es) CallForTender"""

    def testCFIDates(self):
        """ Test CFI Dates
        """
        self.setRoles('Manager')
        root = self.folder
        today = DateTime()
        _zone = DateTime().timezone()
        cid = root.invokeFactory(type_name='CallForInterest', id="cfi",
                                 title='Call for interest',
                                 openDate=today,
                                 closeDate=today,
                                 applicationDate=today)
        cfi = getattr(root, cid)
        self.failIf(today.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(today != cfi.getEffectiveDate())
        self.failIf(today != cfi.effective())
        self.failIf(today != cfi.expires())
        self.failIf(today.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(today != cfi.getExpirationDate())

        tomorrow = today + 1
        cfi.setCloseDate(tomorrow)
        self.failIf(tomorrow != cfi.getCloseDate())
        self.failIf(tomorrow != cfi.expires())
        self.failIf(tomorrow.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(tomorrow != cfi.getExpirationDate())

        yesterday = today - 1
        cfi.setOpenDate(yesterday)
        self.failIf(yesterday != cfi.getOpenDate())
        self.failIf(yesterday != cfi.effective())
        self.failIf(yesterday.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(yesterday != cfi.getEffectiveDate())

        cfi.setExpirationDate(today)
        self.failIf(today != cfi.expires())
        self.failIf(today.toZone(_zone).ISO() != cfi.ExpirationDate())
        self.failIf(today != cfi.getExpirationDate())
        self.failIf(today != cfi.getCloseDate())

        cfi.setEffectiveDate(today)
        self.failIf(today.toZone(_zone).ISO() != cfi.EffectiveDate())
        self.failIf(today != cfi.getEffectiveDate())
        self.failIf(today != cfi.effective())
        self.failIf(today != cfi.getOpenDate())


def test_suite():
    """ Tests suite
    """
    from unittest import TestSuite, makeSuite

    suite = TestSuite()
    suite.addTest(makeSuite(testCallForTenders))
    return suite
