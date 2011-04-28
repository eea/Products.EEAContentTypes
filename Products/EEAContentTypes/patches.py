from zope.event import notify

from md5 import md5

from collective.monkey.monkey import Patcher
from valentine.linguaflow.events import TranslationObjectUpdate


linguaPatcher = Patcher('LinguaPlone')

#LinguaPlone patches
from Products.LinguaPlone.I18NBaseObject import *

def getTranslations(self):
    """Returns a dict of {lang : [object, wf_state]}, pass on to layer."""
    if self.isCanonical():
        membership = getToolByName(self, 'portal_membership', None)
        anon = membership and membership.isAnonymousUser()
        catalog = getToolByName(self, 'portal_catalog', None)
        if config.CACHE_TRANSLATIONS and \
           getattr(self, '_v_translations', None):
            return self._v_translations
        result = {}
        workflow_tool = getToolByName(self, 'portal_workflow', None)
        if workflow_tool is None:
            # No context, most likely FTP or WebDAV
            result[self.getLanguage()] = [self, None]
            return result
        lang = self.getLanguage()
        state = workflow_tool.getInfoFor(self, 'review_state', None)
        result[lang] = [self, state]
        for obj in self.getBRefs(config.RELATIONSHIP):
            lang = obj.getLanguage()
            state = workflow_tool.getInfoFor(obj, 'review_state', None)
            rid = catalog.getrid('/'.join(obj.getPhysicalPath()))
            is_empty = False
            if rid:
                metadata = catalog.getMetadataForRID(rid)
                is_empty = metadata and metadata.get('is_empty', False)
            if anon and is_empty:
                continue
            result[lang] = [obj, state]
        if config.CACHE_TRANSLATIONS:
            self._v_translations = result
        return result
    else:
        return self.getCanonical().getTranslations()


linguaPatcher.wrap_method(I18NBaseObject, 'getTranslations', getTranslations)

