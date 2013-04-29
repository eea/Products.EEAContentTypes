""" Upgrade to version 6.6
"""
import logging
import os
import csv
import transaction
from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
from Products.CMFCore.utils import getToolByName

logger = logging.getLogger("Products.EEAContentTypes.upgrades")

def cleanup_viewlets(context):
    """ Remove deprecated viewlets #9552
    """
    storage = getUtility(IViewletSettingsStorage)
    skins = (u"EEADesign2006", u"EEADesignCMS")
    manager = u"plone.belowcontentbody"
    for skin in skins:
        hidden = storage.getHidden(manager, skin)
        if u"eea.related_multimedia" in hidden:
            hidden = [viewlet for viewlet in hidden
                      if viewlet != u"eea.related_multimedia"]

            logger.info("Cleanup 'eea.related_multimedia' viewlet "
                        "from hidden: %s -- %s -- %s", skin, manager, hidden)
            storage.setHidden(manager, skin, hidden)

        order = storage.getOrder(manager, skin)
        if u"eea.related_multimedia" in order:
            order = [viewlet for viewlet in hidden
                     if viewlet != u"eea.related_multimedia"]
            logger.info("Cleanup 'eea.related_multimedia' viewlet "
                        "from order: %s -- %s -- %s", skin, manager, hidden)
            storage.setOrder(manager, skin, order)

def update_tags(context):
    """ Update existing tags based on #14383
    """
    logger.info("Updating all tags from the portal...")
    ctool = getToolByName(context, 'portal_catalog')

    data_filename = 'tags_edited_plural.csv'
    file_path = os.path.join(os.path.dirname(__file__), data_filename)

    # CSV columns:
    # "label","gemeturi","glossaryuri","comments","replacewith",
    # "geonames","instructions"
    reader = csv.reader(open(file_path, 'rb'))

    tags_to_update = {}
    tags_to_delete = {}
    for row in reader:
        if row[4] == 'none':
            tags_to_delete[row[0]] = row[4]
        elif row[4]:
            tags_to_update[row[0]] = row[4].strip()

    count = 1

    ### Delete tags
    for idx, tag in enumerate(tags_to_delete):
        brains = ctool.unrestrictedSearchResults(Subject=tag)
        for brain in brains:
            obj = brain.getObject()
            field = obj.getField('subject')
            tags = field.getAccessor(obj)()
            tags = [kw for kw in tags if kw != tag]
            field.getMutator(obj)(tags)
            obj.reindexObject(idxs=['Subject'])

            count += 1
            if count % 200 == 0:
                logger.info('Deleting tags %s/%s. Transaction commit: %s',
                            idx, len(tags_to_delete), count)
                transaction.commit()

    ### Replace tags
    for idx, (tag, new_tag) in enumerate(tags_to_update.items()):
        brains = ctool.unrestrictedSearchResults(Subject=tag)
        for brain in brains:
            obj = brain.getObject()
            field = obj.getField('subject')
            tags = field.getAccessor(obj)()
            tags = [kw for kw in tags if kw != tag]
            if new_tag not in tags:
                tags.append(new_tag)
            field.getMutator(obj)(tags)
            obj.reindexObject(idxs=['Subject'])

            count += 1
            if count % 200 == 0:
                logger.info('Replacing tags %s/%s. Transaction commit: %s',
                            idx, len(tags_to_update), count)
                transaction.commit()

    ### Re-index content types with custom logic for indexing keywords
    count = 1
    brains = ctool.unrestrictedSearchResults(portal_type=
                ['ExternalDataSpec', 'Assessment', 'IndicatorFactSheet'])
    total_count = len(brains)
    for brain in brains:
        obj = brain.getObjects()
        obj.reindexObject(idxs=['Subject'])

            count += 1
            if count % 200 == 0:
                logger.info('Re-indexing %s objects. Transaction commit: %s',
                            total_count, count)
                transaction.commit()

    logger.info("Updating all tags from the portal... DONE")
