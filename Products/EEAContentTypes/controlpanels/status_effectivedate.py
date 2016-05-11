""" Control panel
"""
import logging

from zope.interface import Interface, implements

from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.EEAPloneAdmin.browser.migrate import \
    FixEffectiveDateForPublishedObjects
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class IStatusEffectiveDate(Interface):
    """ Effective Date Status Interface
    """

    def startFixEffectiveDate(self):
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

    def search(self, filters=None):
        """ Search objs without effective date
        """

        log = logging.getLogger("EffectiveDate status:")
        catalog = getToolByName(self.context, 'portal_catalog')
        search_date = DateTime('1001/01/01 00:00:00')
        search_no_effective_date = {
            'query': search_date,
            'range': 'max'
        }
        query = {
            'review_state': "published",
            'Language': "all",
            'effective': search_no_effective_date,
            'show_inactive': True
        }

        if filters:
            query.update(filters)

        log.info("Catalog search start")
        brains = catalog.searchResults(**query)
        log.info("Catalog search ended")

        if brains:
            log.warning(
                "Found %s affected objects", len(brains)
            )
        else:
            log.info("Objects already DONE")

        return brains

    def __call__(self):
        return self.index()

    def getEffectiveDateStatus(self):
        """ Returns the view's main output; getter for
            'self.brains'
        """

        return [{
            'url': b.getURL(),
            'id': b.getId,
            'title': b.Title,
            'type': b.portal_type,
        } for b in self.search()]

    def startFixEffectiveDate(self):
        """ Fix affected objects
        """

        # call FixEffectiveDateForPublishedObjects to fix affected objects
        effective = FixEffectiveDateForPublishedObjects(self.context,
                                                        self.request)
        effective()

        start = self.request.get('start_from_script', None)
        if start:
            return

        return self.index()
