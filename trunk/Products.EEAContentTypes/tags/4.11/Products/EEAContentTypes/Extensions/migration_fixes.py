""" Fixes
"""
from Products.CMFPlone.utils import getToolByName
import cPickle
import transaction
import logging

logger = logging.getLogger("Migration fix")


def write_folder_order(self):
    """ Write folder order
    """
    catalog = getToolByName(self, "portal_catalog")

    ttool = getToolByName(self, 'portal_types')
    cmf_meta_types = ttool.listContentTypes(by_metatype=1)
    def getCMFObjectsSubsetIds(objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)
        """
        return [obj.id for obj in objs if obj.meta_type in cmf_meta_types]

    images = catalog.searchResults(portal_type="Image")
    files = catalog.searchResults(portal_type="File")

    out = open("/tmp/out.pickle", "w")

    parents = set()
    for brain in images + files:
        path = brain.getPath()
        parent = path[:path.rfind('/')]
        parents.add(parent)

    result = {}
    for path in parents:
        logger.info("Recording %s" % path)
        folder = self.restrictedTraverse(path)
        objs = folder.getFolderContents(full_objects=True)
        #objs = [o for o in folder.objectValues() if hasattr(o, 'meta_type')]
        ids = getCMFObjectsSubsetIds(objs)
        result[path] = ids

    cPickle.dump(result, out)
    out.close()

    return "Done export"


def read_folder_order(self):
    """ Folder order
    """
    ttool = getToolByName(self, 'portal_types')
    cmf_meta_types = ttool.listContentTypes(by_metatype=1)
    def getCMFObjectsSubsetIds(objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)
        """
        return [obj.id for obj in objs if obj.meta_type in cmf_meta_types]


    source = open("/tmp/out.pickle")
    result = cPickle.load(source)

    toavoid = [
    '/www/SITE/soer/unpublished-content',
    '/www/SITE/soer/published-future',
    '/www/SITE/cop15/cop15-events',
    ]

    for path, oids in result.items():
        logger.info("Doing path: %s" % path)

        if path in toavoid:
            logger.info("Avoiding path: %s" % path)
            continue

        try:
            parent = self.unrestrictedTraverse(path, default=None)
            if parent == None:
                logger.info("Could not get path: %s" % path)
                continue

        except Exception:
            logger.info("Could not get path: %s" % path)
            continue

        objs = parent.getFolderContents(full_objects=True)
        if oids == getCMFObjectsSubsetIds(objs):
            logger.info("Skipping %s because of the same order" % path)
            continue

        for position, oid in enumerate(oids):
            parent.moveObject(oid, position)
            logger.info("%s: Moving %s to position %s" % (path, oid, position))
            obj = parent[oid]
            try:
                obj.reindexObject()
            except Exception, err:
                logger.debug(err)
                continue

        try:
            parent.reindexObject()
        except Exception, err:
            logger.debug(err)

        transaction.commit()

    source.close()

    return "Done import"

def get_order(self):
    """ Order
    """
    ttool = getToolByName(self, 'portal_types')
    cmf_meta_types = ttool.listContentTypes(by_metatype=1)
    def getCMFObjectsSubsetIds(objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)
        """
        return [obj.id for obj in objs if obj.meta_type in cmf_meta_types]

    objs = [o for o in self.objectValues() if hasattr(o, 'meta_type')]
    return getCMFObjectsSubsetIds(objs)


def get_order_contents(self):
    """ Order contents
    """
    ttool = getToolByName(self, 'portal_types')
    cmf_meta_types = ttool.listContentTypes(by_metatype=1)
    def getCMFObjectsSubsetIds(objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)
        """
        return [obj.id for obj in objs if obj.meta_type in cmf_meta_types]

    objs = self.getFolderContents(full_objects=True)
    return getCMFObjectsSubsetIds(objs)


def set_folder_order(self):
    """Fixes just a folder"""

    ttool = getToolByName(self, 'portal_types')
    cmf_meta_types = ttool.listContentTypes(by_metatype=1)
    def getCMFObjectsSubsetIds(objs):
        """Get the ids of only cmf objects (used for moveObjectsByDelta)
        """
        return [obj.id for obj in objs if obj.meta_type in cmf_meta_types]

    source = open("/tmp/out.pickle")
    result = cPickle.load(source)

    parent = self
    path = '/'.join(parent.getPhysicalPath())
    oids = result[path]

    for position, oid in enumerate(oids):
        parent.moveObject(oid, position)
        logger.info("%s: Moving %s to position %s" % (path, oid, position))
        obj = parent[oid]
        obj.reindexObject()

    parent.reindexObject()

    return "Reorder done"
