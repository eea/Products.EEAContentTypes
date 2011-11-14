""" Monkey patches
"""
from Products.CMFCore.utils import getToolByName
from collective.monkey.monkey import Patcher
from ZODB.POSException import ConflictError
from Products.LinguaPlone import config
from Products.EEAContentTypes.setup.ConfigurationMethods import (
    registerTransforms,
)

eeaPatcher = Patcher('EEA')
linguaPatcher = Patcher('LinguaPlone')

#LinguaPlone patches
from Products.LinguaPlone.I18NBaseObject import I18NBaseObject

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

if not linguaPatcher.is_wrapper_method(getTranslations):
    linguaPatcher.wrap_method(I18NBaseObject, 'getTranslations',
                              getTranslations)

#Kupu patch
#disable kupu transform reinstallation every time config is changed
from Products.kupu.plone import util

def install_transform(self):
    """ Install transforms
    """
    registerTransforms(self, self)

if not eeaPatcher.is_wrapper_method(util.install_transform):
    eeaPatcher.wrap_method(util, 'install_transform', install_transform)


def getPathLanguage(self):
    """Checks if a language is part of the current path."""
    if not hasattr(self, 'REQUEST'):
        return []
    domain = self.REQUEST.get('SERVER_URL') + '/'
    path = self.REQUEST.get('ACTUAL_URL')[len(domain):]
    if len(path) == 2 and not path.endswith('/'):
        path += '/'
    try:
        if len(path) > 2 and path.index('/') == 2:
            if path[:2] in self.getSupportedLanguages():
                return path[:2]
    except ConflictError:
        raise
    except:
        pass
    return None

from Products.PloneLanguageTool import LanguageTool

if not eeaPatcher.is_wrapper_method(LanguageTool.getPathLanguage):
    eeaPatcher.wrap_method(LanguageTool, 'getPathLanguage', getPathLanguage)
