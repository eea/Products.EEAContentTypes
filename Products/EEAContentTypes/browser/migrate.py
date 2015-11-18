""" App module
"""
import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone.protect.interfaces import IDisableCSRFProtection
from zope.interface import alsoProvides

logger = logging.getLogger('Products.EEAContentTypes.browser.migrate')


class MigrateDataProvenances(BrowserView):
    """migrate ds_resolveuid into reference items
    """
    
    def __init__(self, context, request):
        self.context = context
        self.request = request
        alsoProvides(self.request, IDisableCSRFProtection)

    def __call__(self):
        """ call
        """
        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(portal_type="DavizVisualization")

        for brain in brains:
            obj = brain.getObject()
            field = obj.getField('provenances', None)
            if not field:
               continue
            provenances = field.getAccessor(obj)()

            TOMIGRATE = False

            for p in provenances:
                link = p.get('link', None)
                if link and 'ds_resolveuid' in link:
                    TOMIGRATE = True

            if TOMIGRATE:
                logger.info("process migrate %s linked by %s" % (
                    link, obj.absolute_url())
                )
                field.set(obj, provenances)

        return "Success!"

