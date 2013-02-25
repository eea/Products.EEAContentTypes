""" Setup handlers
"""

from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
from Products.Archetypes.utils import shasattr
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IEEAPloneSite
from Products.EEAContentTypes.vocabulary import vocabs
from Products.contentmigration.archetypes import InplaceATItemMigrator
from zope.interface import alsoProvides
import logging

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
        if getattr(p, 'geo_services', None) is None:
            p._setProperty('geo_services', [
                'None', 'Google Maps', 'Yahoo Maps',
                'Mapquest (not implemented)',
                'Microsoft Virtual Earth (not implemented)',
                'EEA GeoNode (not implemented)'], 'lines')
        if getattr(p, 'map_service_to_use', None) is None:
            p._setProperty('map_service_to_use', 'geo_services', 'selection')
        if getattr(p, 'geocoding_service_priority', None) is None:
            p._setProperty('geocoding_service_priority', [
                'Google Maps', 'Yahoo Maps'], 'lines')
        if getattr(p, 'google_key', None) is None:
            p._setProperty('google_key', '', 'string')
        if getattr(p, 'yahoo_key', None) is None:
            p._setProperty('yahoo_key', '', 'string')
        if getattr(p, 'mapquest_key', None) is None:
            p._setProperty('mapquest_key', '', 'string')

        # Map default values
        if getattr(p, 'PointZoom_single', None) is None:
            p._setProperty('PointZoom_single', '', 'string')
        if getattr(p, 'MapLoc_single', None) is None:
            p._setProperty('MapLoc_single', '', 'string')
        if getattr(p, 'MapZoom_single', None) is None:
            p._setProperty('MapZoom_single', '', 'string')
        if getattr(p, 'MapLoc_multi', None) is None:
            p._setProperty('MapLoc_multi', '', 'string')
        if getattr(p, 'MapZoom_multi', None) is None:
            p._setProperty('MapZoom_multi', '', 'string')


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
            p._setProperty('invalidate_cache', [
        'http://webservices.eea.europa.eu/templates_client/invalidate_cache'],
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

        logger.info("adding vocabulary %s" % vkey)

        try:
            atvm.invokeFactory('SimpleVocabulary', vkey)
        except Exception:
            logger.info("Error adding vocabulary %s" % vkey)

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


def add_eeaInternalIps(self, portal):
    """ IPs used by EEA and local dev """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'eea_internal_ips', None)
    if not f_prop:
        print 'adding eea_internal_ips'
        prop_tool.manage_addPropertySheet(
            'eea_internal_ips', 'EEA Internal IPs')

        p = getattr(prop_tool, 'eea_internal_ips', None)
        if p is not None:
            if getattr(p, 'allowed_ips', None) is None:
                p._setProperty('allowed_ips', ['10.92', '10.30', \
                                               '192.168.60', '192.168.61', \
                                               '192.168.62', '192.168.63', \
                                               '192.168.64', '192.168.65', \
                                               '127.0.0.1'], 'lines')


def setupGeocoding(context):
    """ Setup geocoding
    """
    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return
    portal = context.getSite()
    #TODO: plone4 this needs to be adapted for plone.app.caching
    #updateCacheFu(portal, portal)

    # This updates were already ran, we don't need them anymore
    #TODO: this gimmick should be removed and replaced by something proper
    already_ran = False
    if not already_ran:
        add_eeaInternalIps(portal, portal)
        print "not proper"
        #geocodeEvents(portal, portal)


#TODO: plone4, shouldn't this be moved to a GS file?
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
    #configureWorkflow(portal)
    #setupCatalog(portal)
    setupGeographicalProperties(portal, portal)
    setupTemplateServiceProperties(portal, portal)
    setupEEAStaffProperties(portal, portal)
    setupCalendarTypes(portal)
    setupCustomRoles(context, portal)


class InplaceGisMigrator(InplaceATItemMigrator):
    """Migrator for TTW Type to disk based GIS Application
    """
    dst_meta_type="GISMapApplication"
    dst_portal_type="GIS Application"


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
        logger.info("Removed %s transform" % name)
    except AttributeError:
        logger.info("Could not remove %s transform" % name)

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

#this is a migration procedure, not needed for plone4 migration
#def setupCatalog(context):
    #""" Setup catalog
    #"""
    #catalog = getToolByName(context, 'portal_catalog')
    #indexes = [ "getImageCopyright", "getImageNote",
                #"getImageSource", "getNewsTitle",
                #"getQuotationSource", "getQuotationText",
                #"getTeaser", "getUrl", "getVisibilityLevel",]
    #toReIndex = [ index.getId()  for index in catalog.index_objects()
                      #if index.getId() in indexes and index.numObjects() == 0]

    #if toReIndex:
        #print "The following indexes must be re-indexed: %s" \
                #% ', '.join(toReIndex)
        ## Reindex catalog indexes can be time expensive, activate it if needed
        ##catalog.manage_reindexIndex(ids=toReIndex)


#TODO: plone4 this needs to be adapted for plone.app.caching
#def updateCacheFu(self, portal):
    #""" Update CacheFu from 1.2 to 1.2.1 """
    #portal_cache = getToolByName(portal, 'portal_cache_settings', None)
    #if portal_cache:
        #if not hasattr(portal_cache, 'installedversion'):
            #setattr(portal_cache, 'installedversion', '1.2.1')
            #print "portal_cache_settings 'installedversion' property updated"


#TODO: plone4: this is a migration step, it's not needed to be executed
#def geocodeEvents(self, portal):
    #""" geocode events location """
    #import pdb; pdb.set_trace()
    #portal_catalog = getToolByName(portal, 'portal_catalog')
    #portal_calendar = getToolByName(portal, 'portal_calendar')
    #types = portal_calendar.getCalendarTypes()

    #events = portal_catalog(meta_type=types)
    #for brain in events:
        #obj = brain.getObject()
        #decider = getUtility(IGeoPositionDecider, context=obj)
        #decider.run(obj)



