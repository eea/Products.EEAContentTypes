""" Promotion
"""
from zope.interface import implements
from zope.component import adapts, getMultiAdapter
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from Products.NavigationManager.sections.adapters import NavigationSections
from eea.promotion.interfaces import IPromotion
from eea.themecentre.interfaces import IThemeTagging
from Products.NavigationManager.interfaces import INavigationSectionPosition
from Products.EEAContentTypes.content.interfaces import IExternalPromotion


class ThemepageSectionsVocabulary(object):
    """ Voc
    """
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
    """ Promotion
    """
    implements(IPromotion)
    adapts(IExternalPromotion)

    def __init__(self, context):
        self.context = context
        self.is_external = True
        url_adapter = getMultiAdapter((context, context.REQUEST), name='url')
        self.url = url_adapter.listing_url()

    @property
    def locations(self):
        """ Locatons
        """
        ret = []
        if self.display_on_frontpage:
            ret.append(u'Front Page')
        if self.display_on_themepage:
            ret.append(u'Themes')
        return ret

    @property
    def themepage_section(self):
        """ Theme section
        """
        return INavigationSectionPosition(self.context).section

    @property
    def active(self):
        """ Active
        """
        return self.display_on_frontpage or self.display_on_themepage

    @property
    def display_on_frontpage(self):
        """ Display on front page
        """
        # XXX: all external promotions show on the frontpage currently
        return True

    @property
    def display_on_themepage(self):
        """ Display on themepage
        """
        return len(self.themes) > 0

    @property
    def display_globally(self):
        """ Display everywhere
        """
        # XXX: not implemented for external promotions
        pass

    @property
    def display_in_spotlight(self):
        """ Display in spotlight
        """
        # XXX: not implemented for external promotions
        pass

    @property
    def display_on_datacentre(self):
        """ Display in datacentre
        """
        # XXX: not implemented for external promotions
        pass

    @property
    def themes(self):
        """ Themes
        """
        return IThemeTagging(self.context).tags

    @property
    def edit_url(self):
        """ Edit URL
        """
        return self.context.absolute_url() + '/edit'
