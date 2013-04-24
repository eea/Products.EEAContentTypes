""" Upgrade to version 6.6
"""
import logging
from zope.component.hooks import getSite
from zope.component import getUtility
from plone.app.viewletmanager.interfaces import IViewletSettingsStorage
logger = logging.getLogger("Products.EEAContentTypes")

def cleanup_viewlets(context):
    """ Remove deprecated viewlets
    """
    site = getSite()
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
