""" Language
"""
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.PloneLanguageTool.interfaces import ITranslatable
from Products.EEAContentTypes.browser.interfaces import ILanguages
from plone.memoize.ram import cache
import zope.interface

def cacheKey(method, self):
    """ Cache key
    """
    request = self.request
    return (method.__name__, request.get('LANGUAGE', 'en'))


class Languages(BrowserView):
    """ Return different languages for translation of content and for
        local sites.
    """

    zope.interface.implements(ILanguages)

    def getTranslationLanguages(self):
        """ Languages
        """
        pl = getToolByName(self.context, 'portal_languages')
        site_languages = pl.listSupportedLanguages()
        site_languages.sort()
        return site_languages

    def getTranslatedSitesLanguages(self):
        """ Site languages
        """
        languages = self.getTranslationLanguages()

        def _cmp(a, b):
            """ Compare
            """
            cmp_one = a[1]
            cmp_two = b[1]
            if a[0] == 'bg':
                cmp_one = 'B'
            if b[0] == 'bg':
                cmp_two = 'B'
            if a[0] == 'cs':
                cmp_one = 'C'
            if b[0] == 'cs':
                cmp_two = 'C'
            if a[0] == 'el':
                cmp_one = 'Eet'
            if b[0] == 'el':
                cmp_two = 'Eet'
            if a[0] == 'is':
                cmp_one = 'Is'
            if b[0] == 'is':
                cmp_two = 'Is'
            return cmp(cmp_one, cmp_two)

        languages.sort(_cmp)
        exclude = ['ar', 'bs', 'ga', 'mk', 'ru', 'sh', 'sq', 'sr']
        return [lang for lang in languages
                if lang[0] not in exclude]

    @cache(cacheKey)
    def getLocalSites(self):
        """ Local sites using site_properties site_url property or eea fallback
        """
        languages = self.getTranslatedSitesLanguages()
        sites = []

        pprops = getToolByName(self.context, 'portal_properties')
        sprops = pprops.site_properties
        site_url = sprops.getProperty('site_url', 'https://www.eea.europa.eu')
        for lang in languages:
            langcode = lang[0]
            langcode_in_url = langcode if langcode != 'en' else ''
            url = '%s/%s' % (site_url, langcode_in_url)
            sites.append({'lang': lang[1],
                          'langcode': langcode,
                          'url': url})
        return sites


class LanguageSelectorData(BrowserView):
    """ VIEWified languageSelectorData.py from LinguaPlone/skins/
        so we can test it
    """
    
    def has_published_translations(self, context):
        """ check if context has published translations
        """
        published = {}
        translations = context.getTranslations()
        for k, v in translations.items():
            if v[1] == 'published':
                published[k] = v
        if len(published) > 1:
            return published
        else:
            return False

    def data(self):
        """ Data
        """
        context = self.context
        results = []
        putils = getToolByName(self.context, 'plone_utils')
        ptool = getToolByName(self.context, 'portal_properties')
        site_properties = getattr(ptool, 'site_properties', None)
        typesUsingViewUrl = site_properties.getProperty(
            'typesUseViewActionInListings', ())

        translations = {}  # lang:[object, wfstate]

        if ITranslatable.providedBy(context):
            translations = context.getTranslations()

        # Check if parent container has translations
        # even if the default page has none.
        if len(translations) == 1 and putils.isDefaultPage(context):
            my_container = aq_parent(aq_inner(context))
            if ITranslatable.providedBy(my_container):
                translations = my_container.getTranslations()

        if context.portal_membership.isAnonymousUser():
            translations = self.has_published_translations(context)
            if not translations:
                return results

        langtool = context.portal_languages
        site_languages = langtool.listSupportedLanguages()
        if hasattr(context, 'getLanguage'):
            current_language = context.getLanguage()
        else:
            current_language = langtool.getPreferredLanguage()

        site_languages.sort()
        for code, name in site_languages:
            if not isinstance(name, unicode):
                name = unicode(name, 'utf-8')
            current = code == current_language
            available = translations.has_key(code)
            alt = context.translate(msgid='label_switch_language_to',
                                    default=u'Switch language to ${language}',
                                    mapping={'language': name},
                                    domain='linguaplone')

            lingua_state = None
            if available:
                translation = translations[code][0]

                if putils.isDefaultPage(translation):
                    # Check if parent container has translation and
                    # in this case redirect to it.
                    my_container = aq_parent(aq_inner(translation))
                    if ITranslatable.providedBy(my_container):
                        if my_container.getTranslations().has_key(code):
                            translation = my_container

                url = translation.absolute_url()
                if translation.portal_type in typesUsingViewUrl:
                    url += '/view'

                wf = context.portal_workflow
                lingua_state = wf.getInfoFor(translation, 'review_state',
                                             None, 'linguaflow')

            elif context.Language() == '':
                url = context.absolute_url()
                alt += context.translate(
                    msgid='label_content_is_language_neutral',
                    default=u' (Content is language neutral)',
                    domain='linguaplone')
            else:
                url = context.absolute_url() + '/not_available_lang'
                alt += context.translate(
                    msgid='label_content_translation_not_available',
                    default=u' (Content translation not available)',
                    domain='linguaplone')

            results.append({'Language': code, 'Title': name, 'current': current,
                            'flag': langtool.getFlagForLanguageCode(code),
                            'available': available, 'change_url': url,
                            'alt': alt, 'invalid': lingua_state == 'invalid'})
        return results
