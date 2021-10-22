""" Upgrade to version 20.3
"""
import logging
from plone.api import portal

logger = logging.getLogger("Products.EEAContentTypes.upgrades")


def update_object_searchabletext(context):
    """ Update faq objects for SearchableText 
    """
    ### Re-index faq content types
    logger.info("Updating FAQ SearchableText index ...")

    catalog = portal.get_tool(name='portal_catalog')
    query = {'portal_type': [ 'helpcenter_faq' ]}
    results = catalog.searchResults(**query)
    logger.info('Got %s results.' % len(results))

    for brain in results:
        obj = brain.getObject()
        obj.reindexObject()

    logger.info("Updating FAQ SearchableText index ... DONE")
