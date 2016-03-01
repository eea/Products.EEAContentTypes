""" Control panel
"""
import logging
from DateTime import DateTime
from Products.Five import BrowserView
from zope.interface import Interface, implements
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.browser.migrate import \
    FixEffectiveDateForPublishedObjects


class IStatusEffectiveDate(Interface):
    """ Effective Date Status Interface
    """

    def startFixEffectiveDate():
        """ Fix affected objects
        """


class StatusEffectiveDate(BrowserView):
    """ Effective Date Status
    """

    implements(IStatusEffectiveDate)
    index = ViewPageTemplateFile("status_effectivedate.pt")

    def __init__(self, context, request):
        super(StatusEffectiveDate, self).__init__(context, request)
        self.logger = logging.getLogger(
            "EffectiveFix")

    def search(self, filters={}):
        """ Search objs without effective date
        """

        catalog = getToolByName(self.context, 'portal_catalog')
        no_effective_date = DateTime('1000/01/01 00:00:00')
        query = {
            'review_state': "published",
            'Language': "all",
            'effective': no_effective_date,
            'show_inactive': True
        }

        if filters:
            query.update(filters)

        self.logger.info("*** Catalog search start")
        brains = catalog.searchResults(**query)
        self.logger.info("*** Catalog search ended")

        if brains:
            self.logger.warning(
                "*** Found %s affected objects" % len(brains)
            )
        else:
            self.logger.info("*** Objects already DONE")

        return brains

    def __call__(self):
        return self.index()

    def getEffectiveDateStatus(self):
        """ Returns the view's main output; getter for
            'self.brains'
        """

        return [{
            'url': b.getURL(),
            'title': b.Title,
            'type': b.portal_type,
        } for b in self.search()]

    def startFixEffectiveDate(self):
        """ Fix affected objects
        """

        # call FixEffectiveDateForPublishedObjects to fix affected objects
        effective = FixEffectiveDateForPublishedObjects(self.context, self.request)
        effective()

        start = self.request.get('start_from_script', None)
        if not start:
            return

        return self.index()