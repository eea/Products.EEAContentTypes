""" evolve script
"""

from eea.versions.versions import _random_id
import logging

logger = logging.getLogger('Products.EEAContentTypes.migration')


def evolve(context):
    """ Migrate versionIds for non-Archetypes objects that don't have them set
    """
    p_types = [
        'Newsletter',
        'NewsletterTheme'
        ]
        
    cat = context.portal_catalog
    brains = cat.searchResults(portal_type=p_types, Language="all")

    for brain in brains:
        obj = brain.getObject()
        versionId = _random_id(obj)
        obj.__annotations__['versionId'] = versionId
        obj.reindexObject()
        msg = "Migrated versionId storage (empty storage) for %s (%s)" % \
                (obj.absolute_url(), versionId)
        logger.info(msg)
    
    logger.info("Finished migration of PG content types version ids")
