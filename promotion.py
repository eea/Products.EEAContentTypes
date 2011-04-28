from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.schema.vocabulary import SimpleTerm, SimpleVocabulary
from zope.app.schema.vocabulary import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from Products.NavigationManager.sections import NavigationSections
from eea.promotion.interfaces import IPromotion
from eea.themecentre.interfaces import IThemeTagging
from Products.NavigationManager.sections import INavigationSectionPosition
from Products.NavigationManager.browser.navigation import getApplicationRoot
from Products.EEAContentTypes.content.interfaces import IExternalPromotion


def getPromotionFolder(context):
    portal_properties = getToolByName(context, 'portal_properties')
    frontpage_properties = getattr(portal_properties, 'frontpage_properties')
    promotionFolder = frontpage_properties.getProperty('promotionFolder', None)
    if not promotionFolder.startswith('/'):
        plone_utils = getToolByName(context, 'plone_utils')
        folder = context
        if plone_utils.isDefaultPage(context):
            folder = aq_parent(aq_inner(context))
        promotionFolder = '%s/%s' % ('/'.join(folder.getPhysicalPath()), promotionFolder)
    return promotionFolder


class FrontpageSectionsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context, testPromotionFolder=None):
        if hasattr(context, 'context'):
            context = context.context
        promotionFolder = testPromotionFolder or getPromotionFolder(context)
        portal = getToolByName(context, 'portal_url').getPortalObject()
        folder = portal.restrictedTraverse(promotionFolder)
        terms = []
        for i in folder.listFolderContents():
            value = '/'.join(i.getPhysicalPath())
            token = i.id
            title = i.title
            terms.append(SimpleTerm(value, token, title))
        return SimpleVocabulary(terms)

FrontpageSectionsVocabularyFactory = FrontpageSectionsVocabulary()


class ThemepageSectionsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self, context):
        if hasattr(context, 'context'):
            context = context.context
        themes = context.restrictedTraverse('/www/SITE/themes')
        sections = NavigationSections(themes)
        left = sections.left
        for i in left:
            i.title = u'(Left) ' + i.title
        right = sections.right
        for i in right:
            i.title = u'(Right) ' + i.title
        return SimpleVocabulary(left + right)

ThemepageSectionsVocabularyFactory = ThemepageSectionsVocabulary()


class Promotion(object):
    implements(IPromotion)
    adapts(IExternalPromotion)

    def __init__(self, context):
        self.context = context
        self.is_external = True
        url_adapter = getMultiAdapter((context, context.REQUEST), name='url')
        self.url = url_adapter.listing_url()

    @property
    def locations(self):
        ret = []
        if self.display_on_frontpage:
            ret.append(u'Front Page')
        if self.display_on_themepage:
            ret.append(u'Themes')
        return ret

    @property
    def themepage_section(self):
        return INavigationSectionPosition(self.context).section

    @property
    def frontpage_section(self):
        if self.display_on_frontpage:
            return '/'.join(self.context.getPhysicalPath()[:-1])

    @property
    def active(self):
        return self.display_on_frontpage or self.display_on_themepage

    @property
    def display_on_frontpage(self):
        # If we're in quicklinks, we should show on front page
        promofolder = getPromotionFolder(getApplicationRoot(self.context))
        category_parent_folder = '/'.join(self.context.getPhysicalPath()[:-2])
        return category_parent_folder == promofolder

    @property
    def display_on_themepage(self):
        return len(self.themes) > 0

    @property
    def display_globally(self):
        pass

    @property
    def themes(self):
        return IThemeTagging(self.context).tags

    @property
    def edit_url(self):
        return self.context.absolute_url() + '/edit'
