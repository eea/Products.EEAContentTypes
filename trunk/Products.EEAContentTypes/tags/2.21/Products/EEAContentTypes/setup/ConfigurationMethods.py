import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getUtility
from OFS.PropertyManager import PropertyManager
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import AddPortalMember
from Products.CMFCore.Expression import Expression
from Products.CMFPlone.migrations.migration_util import safeEditProperty
from Acquisition import aq_get
from AccessControl import Permissions
from Products.SiteErrorLog.SiteErrorLog import manage_addErrorLog
from DateTime import DateTime
from Products.GroupUserFolder.GroupsToolPermissions import ViewGroups

from zLOG import INFO
from Products.CMFPlone.setup.SetupBase import SetupWidget
from Globals import package_home
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.transforms import ProtectEmail
from Products.EEAContentTypes.transforms import InternalLinkView
from Products.EEAContentTypes.transforms import TranslationResolveUid
from Products.EEAContentTypes.setup.remap import remap_workflow
from Products.EEAContentTypes.content.interfaces import IGeoPositionDecider
from Products.PortalTransforms.chain import TransformsChain, chain
from Products.kupu.plone import util
from collective.monkey.monkey import Patcher
eeaPatcher = Patcher('EEA')

def registerTransforms(self, portal):
    ptr = getToolByName(portal, 'portal_transforms')
    if 'protect_email' not in ptr.objectIds():
        ptr.registerTransform(ProtectEmail())
    if 'internallink_view' not in ptr.objectIds():
        ptr.registerTransform(InternalLinkView())
    if 'translation_resolveuid' not in ptr.objectIds():
        ptr.registerTransform(TranslationResolveUid())

    # we need to manually install kupu defaults since we patch away that method
    eeaPatcher.call(util,'install_transform', portal)

    chain_ = ['translation_resolveuid', 'html-to-captioned', 'captioned-to-html', 'safe_html',
              'protect_email', 'internallink_view']
    html_eea_chain = getattr(ptr, 'html_eea_chain', None)
    if html_eea_chain is not None and chain_ != html_eea_chain._object_ids:
        ptr._unmapTransform(html_eea_chain)
        # we need to suppress the ObjectWillBeRemovedEvent, otherwise
        # there will be infinite recursion for some unknown reason
        ptr._delObject('html_eea_chain', suppress_events=True)
    if 'html_eea_chain' not in ptr.objectIds():
        transform = TransformsChain('html_eea_chain', 'protect emails after safe_html',
                                    chain_)
        c = chain()
        for id in transform._object_ids:
            object = getattr(ptr, id)
            c.registerTransform(object)
        transform.inputs = c.inputs
        transform.output = c.output
        transform._chain = c
        ptr._setObject('html_eea_chain', transform)
        ptr._mapTransform(transform)

    # Set policy
    policies = [(mimetype, required) for (mimetype, required) in ptr.listPolicies()]
    # remove the policy that's always added by kupu installation
    if ('text/x-html-safe', ('html-to-captioned',)) in policies:
        ptr.manage_delPolicies(['text/x-html-safe'])
    if ('text/x-html-safe', ('html_eea_chain',)) not in policies:
        ptr.manage_addPolicy('text/x-html-safe', ['html_eea_chain'])

def migrateCFT(self, portal):
    for cft in getattr(portal,'tenders-X').contentValues('CallForTender')[:10]:
        if hasattr(cft, 'nextDoc'):
            doc = getattr(cft, cft.nextDoc)
            cft.setCallForId( cft.Title() )
            cft.setTitle( doc.Title() )
            cft.setText( doc.getText())
            cft.manage_delObjects(cft.nextDoc)
            del cft.nextDoc

def setupTopic(self, portal):
    atct = portal.portal_atct.addMetadata('getTeaser', 'Teaser', 'Teaser for frontpage items', enabled=True)

def registerFrontPageViews(self, portal):
    pt = getToolByName(portal, 'portal_types')
    plonesite = pt.getTypeInfo('Plone Site')
    views = ['frontpage_view']
    for view in plonesite.view_methods:
        if view not in views:
            views.append(view)
    plonesite.view_methods = views
    plonesite.default_view = 'frontpage_view'

def geocodeEvents(self, portal):
    """ geocode events location """
    portal_catalog = getToolByName(portal, 'portal_catalog')
    portal_calendar = getToolByName(portal, 'portal_calendar')
    types = portal_calendar.getCalendarTypes()

    events = portal_catalog(meta_type=types)
    for brain in events:
        obj = brain.getObject()
        decider = getUtility(IGeoPositionDecider, context=obj)
        decider.run(obj)

def eeaInternalIps(self, portal):
    """ IPs used by EEA and local dev """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'eea_internal_ips', None)
    if not f_prop:
        print 'adding eea_internal_ips'
        prop_tool.manage_addPropertySheet('eea_internal_ips', 'EEA Internal IPs')

        p = getattr(prop_tool, 'eea_internal_ips', None)
        if p is not None:
            if getattr(p, 'allowed_ips', None) is None:
                p._setProperty('allowed_ips', ['10.92', '10.30', \
                                               '192.168.60', '192.168.61', \
                                               '192.168.62', '192.168.63', \
                                               '192.168.64', '192.168.65', \
                                               '127.0.0.1'], 'lines')

def setupGeographicalProperties(self, portal):
    """ sets up the default propertysheet for geographical related stuff """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'geographical_properties', None)

    # Reset properties if we are in development

    #development = getattr(f_prop,'development', None)
    #if not f_prop or development:
    #    if development:
    #        prop_tool.manage_delObjects(['geographical_properties'])
    #    print 'adding geographical_properties'
    #    prop_tool.manage_addPropertySheet('geographical_properties', 'EEA Geographical properties')

    if not f_prop:
        print 'adding geographical_properties'
        prop_tool.manage_addPropertySheet('geographical_properties', 'EEA Geographical properties')

    p = getattr(prop_tool, 'geographical_properties', None)
    if p is not None:
        if getattr(p, 'geo_services', None) is None:
            p._setProperty('geo_services', ['None', 'Google Maps', 'Yahoo Maps', 'Mapquest (not implemented)', 'Microsoft Virtual Earth (not implemented)', 'EEA GeoNode (not implemented)'], 'lines')
        if getattr(p, 'map_service_to_use', None) is None:
            p._setProperty('map_service_to_use', 'geo_services', 'selection')
        if getattr(p, 'geocoding_service_priority', None) is None:
            p._setProperty('geocoding_service_priority', ['Google Maps', 'Yahoo Maps'], 'lines')
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
    """ sets up the default propertysheet for template service invalidate cache """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'template_service', None)
    # reset properties if we are in development
    development = getattr(f_prop,'development', None)
    if not f_prop or development:
        if development:
            prop_tool.manage_delObjects(['template_service'])

        print 'adding template_service'
        prop_tool.manage_addPropertySheet('template_service', 'Template service - invalidate cache')

    p = getattr(prop_tool, 'template_service', None)
    if p is not None:
        if getattr(p, 'invalidate_cache', None) is None:
            p._setProperty('invalidate_cache', ['http://webservices.eea.europa.eu/templates_client/invalidate_cache'], 'lines')

def setupEEAStaffProperties(self, portal):
    """ sets up the default propertysheet for EEA staff """
    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'eeastaff_properties', None)
    # reset properties if we are in development
    development = getattr(f_prop,'development', None)
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

def setupFrontpageProperties(self, portal):
    """ sets up the default propertysheet for frontpage  related stuff """

    prop_tool = portal.portal_properties
    f_prop = getattr(prop_tool, 'frontpage_properties', None)
    # reset properties if we are in development
    development = getattr(f_prop,'development', None)
    if not f_prop or development:
        if development:
            prop_tool.manage_delObjects(['frontpage_properties'])

        prop_tool.manage_addPropertySheet('frontpage_properties', 'EEA Frontpage properties')
        p=prop_tool.frontpage_properties

        p._setProperty('promotionFolder', '/www.eea.europa.eu/promotions', 'string')
        p._setProperty('noOfHigh', 3, 'int')
        p._setProperty('noOfMedium', 4, 'int')
        p._setProperty('noOfLow', 10, 'int')
        p._setProperty('development', True, 'boolean')

def setupATVocabularies(self, portal):
    """ Installs all AT-based Vocabularies """

    from Products.ATVocabularyManager.config import TOOL_NAME as ATVOCABULARYTOOL
    from vocabularies import vocabs

    vkeys = vocabs.keys()
    atvm = getToolByName(portal, ATVOCABULARYTOOL, None)
    if atvm is None:
        return

    for vkey in vkeys:

        if hasattr(atvm, vkey):
            continue

        print "adding vocabulary %s" % vkey

        atvm.invokeFactory('SimpleVocabulary', vkey)
        vocab = atvm[vkey]
        for (ikey, value) in vocabs[vkey]:
            vocab.invokeFactory('SimpleVocabularyTerm', ikey)
            vocab[ikey].setTitle(value)

def migrateWorkflow(self, portal):
    """ remap states in following content types to the new workflow """
    type_ids = [ 'Document', 'Event', 'Favorite', 'File', 'FlashFile',
                 'HelpCenter', 'Image','Link', 'News Item', 'NewsletterTheme',
                 'NewsletterTopic', 'Promotion', 'RichTopic', 'HelpCenterFAQ',
                 'Highlight']

    wt = getToolByName(portal, 'portal_workflow')
    workflows = { 'Highlight' : wt.frontpage_workflow }

    state_maps = { 'default': { 'visible' : 'visible',
                              'published' : 'published',
                              'private' : 'private',
                              'pending' : 'webqa_pending',
                              'retracted' : 'retracted' },
                  'Highlight': { 'visible' : 'visible',
                                'published' : 'published',
                                'private' : 'private',
                                'pending' : 'visible',
                                'retracted' : 'retracted' },
                  }

    remap_workflow(portal, type_ids, "(Default)", state_maps, workflows=workflows)

def setupThemesDataCentres(self, portal):
    from Products.NavigationManager.sections import INavigationSectionPosition
    for themeId in ['air', 'biodiversity', 'climate', 'landuse', 'water']:
        print 'setting up dc document in %s' % themeId
        themeItem = portal['SITE']['themes'][themeId]

        # Make sure there's a 'dc' page/document
        if not hasattr(themeItem, 'dc'):
            #print 'dc folder already exists in %s, deleting it' % themeId
            #themeItem.manage_delObjects([themeItem.dc.getId()])
            themeItem.invokeFactory('Document', id='dc')

        dcItem = themeItem.dc
        dcItem.setTitle('Data centre overview')
        dcItem.setLayout('dc_view')
        INavigationSectionPosition(dcItem).section = 'data-center-services'

        # Make sure it's published
        workflow = portal.portal_workflow
        try:
            workflow.doActionFor(dcItem, 'publish')
        except:
            pass

        dcItem.reindexObject()

def fixThemes(self, portal):
    import logging
    from eea.themecentre.interfaces import IThemeTagging
    from zope.component import queryAdapter
    logger = logging.getLogger('Themes FIX')
    ctool = getToolByName(portal, 'portal_catalog')
    themes = ctool.Indexes['getThemes'].uniqueValues()
    bad_themes = []
    for theme in themes:
        if theme is None:
            bad_themes.append(theme)
        elif theme in ('', u''):
            bad_themes.append(theme)
        elif theme.startswith(' ') or theme.endswith(' '):
            bad_themes.append(theme)

    logger.info('Fixing themes ... STARTED')
    logger.info('Found bad themes: %s', bad_themes)
    brains = ctool(getThemes={'query': bad_themes, 'operator': 'or'}, Language='all')
    for brain in brains:
        old_themes = brain.getThemes
        new_themes = filter(None, old_themes)
        new_themes = [theme.strip() for theme in new_themes if theme]
        doc = brain.getObject()
        tagging = queryAdapter(doc, IThemeTagging)
        if not tagging:
            continue

        logger.info('Fixing themes for: %s, old themes: %s, new themes: %s',
                    brain.getURL(), old_themes, new_themes)
        try:
            tagging.tags = new_themes
        except Exception, err:
            logger.exception(err)
            continue
    logger.info('Fixing themes ... DONE')


def setupFolderishViewMethods(self, portal):
    for type in ['Folder', 'Topic', 'RichTopic']:
        type = getattr(portal.portal_types, type)
        view_methods = list(type.getProperty('view_methods'))
        for view_method in ['subfolder_view', 'smart_view']:
            if not view_method in view_methods:
                print "adding '%s' view method to type '%s'" % (view_method, type)
                view_methods.append(view_method)
        view_methods = list(set(view_methods)) # Filter out any duplicates
        type.manage_changeProperties(view_methods=view_methods)

def importAlljQueryProfiles(self, portal):
    portal_setup = portal.portal_setup
    profiles = [ # See eea.jquery.profiles.zcml
        '01-jquery',
        '02-ui',
        '03-ajaxfileupload',
        '04-bbq',
        '05-cookie',
        '06-fancybox',
        '07-flashembed',
        '08-galleryview',
        '09-jqzoom',
        '10-jstree',
        '11-reflection',
        '12-select2uislider',
        '13-splitter',
        '14-tagcloud',
        '15-tools',
    ]
    for profile in profiles:
        portal_setup.setImportContext('profile-eea.jquery:%s' % profile)
        res = portal_setup.runAllImportSteps()
        messages = res.get('messages', {})
        output = [message for message in messages.values() if message]
        print '\n'.join(output)


functions = {
    'Set default frontpage properties':setupFrontpageProperties,
    'Set default geographical properties':setupGeographicalProperties,
    'Register frontpage views':registerFrontPageViews,
    'Install default AT Vocabularies':setupATVocabularies,
    'setupTopic' : setupTopic,
    'migrateCFT' : migrateCFT,
    'registerTransforms' : registerTransforms,
    'migrateWorkflow' : migrateWorkflow,
    'setupThemesDataCentres' : setupThemesDataCentres,
    'setupFolderishViewMethods': setupFolderishViewMethods,
    'importAlljQueryProfiles': importAlljQueryProfiles,
    'Fix inconsistent themes': fixThemes,
    }

class EEAContentSetup(SetupWidget):
    """ """

    type = 'EEA Content Setup'

    description = """ This saves you time! """

    functions = functions

    def setup(self):
        pass

    def delItems(self, fns):
        out = []
        out.append(('Currently there is no way to remove a function', INFO))
        return out

    def addItems(self, fns):
        out = []
        for fn in fns:
            self.functions[fn](self, self.portal)
            out.append(('Function %s has been applied' % fn, INFO))
        return out

    def installed(self):
        return []

    def available(self):
        """ Go get the functions """
        return self.functions.keys()

def configureWorkflow(portal):
    """ configure what can't be configured with generic setup. """
    wf = getToolByName(portal, 'portal_workflow')
    if wf is not None:
        wf['eea_default_workflow'].manager_bypass = True

def setupCatalog(context):
    catalog = getToolByName(context, 'portal_catalog')
    indexes = [ "getImageCopyright", "getImageNote",
                "getImageSource", "getNewsTitle",
                "getQuotationSource", "getQuotationText",
                "getTeaser", "getUrl", "getVisibilityLevel",]
    toReIndex = [ index.getId()  for index in catalog.index_objects()
                      if index.getId() in indexes and index.numObjects() == 0]

    if toReIndex:
        print "The following indexes must be re-indexed: %s" % ', '.join(toReIndex)
        # Reindex catalog indexes can be time expensive, activate it if needed
        #catalog.manage_reindexIndex(ids=toReIndex)

def setupCalendarTypes(portal):
    portal_calendar = getToolByName(portal, 'portal_calendar')
    types = portal_calendar.getCalendarTypes()
    if 'QuickEvent' not in types:
        portal_calendar.edit_configuration(types + ('QuickEvent',),
                                           portal_calendar.getUseSession())

def setupGeocoding(context):
    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return
    portal = context.getSite()
    updateCacheFu(portal, portal)

    # This updates were already ran, we don't need them anymore
    already_ran = True
    if not already_ran:
        eeaInternalIps(portal, portal)
        geocodeEvents(portal, portal)

def updateCacheFu(self, portal):
    """ Update CacheFu from 1.2 to 1.2.1 """
    portal_cache = getToolByName(portal, 'portal_cache_settings', None)
    if portal_cache:
        if not hasattr(portal_cache, 'installedversion'):
            setattr(portal_cache, 'installedversion', '1.2.1')
            print "portal_cache_settings 'installedversion' property updated"

def setupVarious(context):
    # only run this step if we are in EEAContentTypes profile
    # learned from Aspelis book, Professional Plone Development
    if context.readDataFile('eeacontenttypes_various.txt') is None:
        return

    portal = context.getSite()
    setupATVocabularies(portal, portal)
    configureWorkflow(portal)
    setupCatalog(portal)
    setupGeographicalProperties(portal, portal)
    setupTemplateServiceProperties(portal, portal)
    setupEEAStaffProperties(portal, portal)
    setupCalendarTypes(portal)
    registerTransforms(portal, portal)
