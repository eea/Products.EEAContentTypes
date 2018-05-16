""" Setup handlers
"""

import logging

from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.contentmigration.archetypes import InplaceATItemMigrator
from Products.EEAContentTypes.interfaces import IEEAPloneSite
from Products.EEAContentTypes.vocabulary import vocabs
from zope.interface import alsoProvides

logger = logging.getLogger("Products.EEAContentTypes")


def setupGeographicalProperties(self, portal):
    """ sets up the default propertysheet for geographical related stuff """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'geographical_properties', None)

    if not f_prop:
        print 'adding geographical_properties'
        prop_tool.manage_addPropertySheet(
            'geographical_properties', 'EEA Geographical properties')

    p = getattr(prop_tool, 'geographical_properties', None)
    if p is not None:
        if getattr(p, 'google_key', None) is None:
            p._setProperty('google_key', '', 'string')


def setupTemplateServiceProperties(self, portal):
    """ sets up the default propertysheet for template service invalidate cache
    """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'template_service', None)
    # reset properties if we are in development
    development = getattr(f_prop, 'development', None)
    if not f_prop or development:
        if development:
            prop_tool.manage_delObjects(['template_service'])

        print 'adding template_service'
        prop_tool.manage_addPropertySheet('template_service',
                                          'Template service - invalidate cache')

    p = getattr(prop_tool, 'template_service', None)
    if p is not None:
        if getattr(p, 'invalidate_cache', None) is None:
            p._setProperty(
                'invalidate_cache', [
                    'http://webservices.eea.europa.eu/templates_client/'
                    'invalidate_cache'],
                'lines')


def setupEEAStaffProperties(self, portal):
    """ sets up the default propertysheet for EEA staff """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'eeastaff_properties', None)
    # reset properties if we are in development
    development = getattr(f_prop, 'development', None)
    if not f_prop or development:
        if development:
            prop_tool.manage_delObjects(['eeastaff_properties'])

        print 'adding eeastaff_properties'
        prop_tool.manage_addPropertySheet('eeastaff_properties', 'EEA Staff')

    p = getattr(prop_tool, 'eeastaff_properties', None)
    if p is not None:
        if getattr(p, 'organisations', None) is None:
            p._setProperty('organisations', [], 'lines')
        if getattr(p, 'eeastaff_fs', None) is None:
            p._setProperty('eeastaff_fs', 'eeastaff.xml', 'string')
        if getattr(p, 'eeastaff_cms', None) is None:
            p._setProperty('eeastaff_cms', 'eeastaff', 'string')


def setupATVocabularies(self, portal):
    """ Installs all AT-based Vocabularies """

    vkeys = vocabs.keys()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        logger.info("Products.ATVocabularyManager is NOT installed")
        return

    for vkey in vkeys:

        if shasattr(atvm, vkey):
            continue

        logger.info("adding vocabulary %s", vkey)

        try:
            atvm.invokeFactory('SimpleVocabulary', vkey)
        except Exception:
            logger.info("Error adding vocabulary %s", vkey)

        vocab = atvm[vkey]
        for (ikey, value) in vocabs[vkey]:
            vocab.invokeFactory('SimpleVocabularyTerm', ikey)
            vocab[ikey].setTitle(value)


def setupCalendarTypes(portal):
    """ Setup calendar types
    """
    portal_calendar = getToolByName(portal, 'portal_calendar')
    types = portal_calendar.getCalendarTypes()
    if 'QuickEvent' not in types:
        portal_calendar.edit_configuration(types + ('QuickEvent',),
                                           portal_calendar.getUseSession())


def setupGeocoding(context):
    """ Setup geocoding
    """
    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return
    portal = context.getSite()
    # TODO: plone4 this needs to be adapted for plone.app.caching
    # updateCacheFu(portal, portal)

    # This updates were already ran, we don't need them anymore
    # TODO: this gimmick should be removed and replaced by something proper
    already_ran = False
    if not already_ran:
        print "not proper"
        # geocodeEvents(portal, portal)


# TODO: plone4, shouldn't this be moved to a GS file?
def setupCustomRoles(self, portal):
    """ Setup custom roles
    """
    roles = list(portal.acl_users.portal_role_manager.listRoleIds())
    newRoles = ['Editor', 'CommonEditor', 'ProofReader',
                'ContentManager', 'WebReviewer']
    for role in newRoles:
        if role not in roles:
            portal.acl_users.portal_role_manager.addRole(role)


def setupVarious(context):
    """ Setup
    """
    # only run this step if we are in EEAContentTypes profile
    # learned from Aspelis book, Professional Plone Development
    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return

    portal = context.getSite()
    setupATVocabularies(portal, portal)
    # configureWorkflow(portal)
    # setupCatalog(portal)
    setupGeographicalProperties(portal, portal)
    setupTemplateServiceProperties(portal, portal)
    setupEEAStaffProperties(portal, portal)
    setupCalendarTypes(portal)
    setupCustomRoles(context, portal)


class InplaceGisMigrator(InplaceATItemMigrator):
    """Migrator for TTW Type to disk based GIS Application
    """
    dst_meta_type = "GISMapApplication"
    dst_portal_type = "GIS Application"


def upgrade_gisapplication(site):
    """Upgrade handler for gisapplication
    """

    logger.info("Started migration of ATLink based GIS Application")
    catalog = getToolByName(site, 'portal_catalog')
    brains = catalog.searchResults(meta_type="ATLink",
                                   portal_type="GIS Application")

    for brain in brains:
        obj = brain.getObject()
        migrator = InplaceGisMigrator(obj)
        migrator.migrate()
        logger.info("Migrated ATLink to GIS Application for %s", migrator.new)

    logger.info("Finished migration of ATLink based GIS Application")


def migrate_gisapplication(context):
    """Migrate GIS Application content from ATLink to its own class
    """

    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return
    site = context.getSite()
    upgrade_gisapplication(site)


def upgrade_plonesite_interface(context):
    """Make the Plone site implement the IEEAPloneSite interface
    """

    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return
    site = context.getSite()
    alsoProvides(site, IEEAPloneSite)
    logger.info("Added IEEPloneSite to interfaces provided by Plone root")


def unregisterTransform(site, name):
    """ Remove portal transform
    """
    transforms = getToolByName(site, 'portal_transforms')
    try:
        transforms.unregisterTransform(name)
        logger.info("Removed %s transform", name)
    except AttributeError:
        logger.info("Could not remove %s transform", name)


def unregister_email_transform(site):
    """ Remove protect_email transform
    """
    unregisterTransform(site, 'protect_email')


def fix_html_eea_chain_transform(site):
    """ Remove from html_eea_chain transform chain absolete
        transforms like html-to-captioned, captioned-to-html
        and protect_email
    """
    transforms = getToolByName(site, 'portal_transforms')
    html_eea_chain = getattr(transforms, 'html_eea_chain')
    html_eea_chain.manage_delObjects(['html-to-captioned',
                                      'captioned-to-html',
                                      'protect_email'])
    logger.info("Fixed html_eea_chain transform chain")
