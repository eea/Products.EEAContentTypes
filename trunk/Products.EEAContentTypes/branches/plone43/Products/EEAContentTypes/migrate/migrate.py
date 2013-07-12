""" Migrate EEA Content-types view controller
"""
import logging
import transaction
from zope.component import queryMultiAdapter
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
logger = logging.getLogger('EEAContentTypes.migrate')

class Migrate(BrowserView):
    """ Run migration for all content-types
    """
    def _redirect(self, msg='', to='@@migrate-eea2blobs'):
        """ Return or redirect
        """
        logger.info(msg)

        if not to:
            return msg

        if not self.request:
            return msg

        if msg:
            IStatusMessage(self.request).addStatusMessage(str(msg), type='info')
        self.request.response.redirect(to)
        return msg

    def _migrate(self, form):
        """ Run migration
        """
        types = form.get('types', ())
        if not types:
            msg = 'You have to select at least one Portal type to migrate'
            return self._redirect(msg)

        ctool = getToolByName(self.context, 'portal_catalog')
        brains = ctool(portal_type=types, Language='all')

        length = len(brains)
        logger.info("Migrating %s documents Image to Blob. "
                    "Selected EEA Content Types: %s",
                    length, ', '.join(types))

        count = 0
        for brain in brains:
            doc = brain.getObject()
            migrate = queryMultiAdapter((doc, self.request),
                                        name=u'migrate2blobs')
            migrate()
            if migrate.status is False:
                continue

            count += 1
            if count % 25 == 0:
                logger.info('Transaction commit: %s', count)
                transaction.commit()

        msg = 'Migration complete. Check the Zope log for more details.'
        return self._redirect(msg)

    @property
    def content_types(self):
        """ Return EEA Content-Types to migrate
        """
        return ("Article", "Highlight", "PressRelease",
                "Promotion", "Speech", 'FlashFile')

    def __call__(self, **kwargs):
        if self.request:
            kwargs.update(self.request.form)

        submitting = kwargs.get('action.submit', None)
        if not submitting:
            return self.index()
        return self._migrate(kwargs)
