from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.schema.vocabulary import SimpleVocabulary #SimpleTerm
from zope.app.schema.vocabulary import IVocabularyFactory
from Products.NavigationManager.sections import NavigationSections
from eea.promotion.interfaces import IPromotion
from eea.themecentre.interfaces import IThemeTagging
from Products.NavigationManager.sections import INavigationSectionPosition
#from Products.NavigationManager.browser.navigation import getApplicationRoot
from Products.EEAContentTypes.content.interfaces import IExternalPromotion


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
    def active(self):
        return self.display_on_frontpage or self.display_on_themepage

    @property
    def display_on_frontpage(self):
        # XXX: all external promotions show on the frontpage currently
        return True

    @property
    def display_on_themepage(self):
        return len(self.themes) > 0

    @property
    def display_globally(self):
        # XXX: not implemented for external promotions
        pass

    @property
    def themes(self):
        return IThemeTagging(self.context).tags

    @property
    def edit_url(self):
        return self.context.absolute_url() + '/edit'
