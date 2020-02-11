""" Upgrade to version 19.0
"""
import logging
import transaction
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("Products.EEAContentTypes.upgrades")


def update_object_provides(context):
    """ Update object_provides index for Data and ExternalDataSpec
    """
    ### Re-index content types with custom logic for indexing keywords
    logger.info("Updating ExternalDataSpec and Data from the portal...")
    ctool = getToolByName(context, 'portal_catalog')
    count = 1
    brains = ctool.unrestrictedSearchResults(
        portal_type=['ExternalDataSpec', 'Data'])
    total_count = len(brains)
    for brain in brains:
        obj = brain.getObject()
        obj.reindexObject(idxs=['object_provides'])

        count += 1
        if count % 200 == 0:
            logger.info('Re-indexing %s objects. Transaction commit: %s',
                        total_count, count)
            transaction.commit()

    logger.info("Updating ExternalDataSpec and Data from the portal... DONE")
