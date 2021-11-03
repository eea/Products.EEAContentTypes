""" Upgrade to version 20.4
"""
import logging
from plone.api import portal

logger = logging.getLogger("Products.EEAContentTypes.upgrades")


def trim_faq_tags(context):
    """ Trim faq tags
    """
    logger.info("Trim FAQ tags ...")

    catalog = portal.get_tool(name='portal_catalog')
    brains = catalog.unrestrictedSearchResults(portal_type='helpcenter_faq')
    logger.info('Got %s results.' % len(brains))

    for brain in brains:
        obj = brain.getObject()
        tags = list(obj.subject)
        tags_check = [val.strip() for val in tags]

        if tags != tags_check:
            obj.subject = tuple(tags_check)
            obj._p_changed = True
            obj.reindexObject()
            logger.info("Trim tags:"+brain.getURL())

    logger.info("Trim FAQ tags ...DONE")