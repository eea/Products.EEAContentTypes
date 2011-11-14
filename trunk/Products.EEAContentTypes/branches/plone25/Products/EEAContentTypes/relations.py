from eea.themecentre.interfaces import IThemeTagging
from zope.component import adapts, queryAdapter
from zope.interface import implements, Interface

from AccessControl import Unauthorized
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IRelations

from p4a.video.interfaces import IVideoEnhanced

class Relations(object):
    implements(IRelations)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def all(self, portal_type=None, constraints=None):
        forwards = self.forwardReferences()
        backs = self.backReferences()
        themes = self.byTheme(portal_type=portal_type,
                              constraints=constraints)

        result = forwards
        uids = [ref.UID() for ref in result]
        result += [back for back in backs if back.UID() not in uids]
        uids = [ref2.UID() for ref2 in result]
        result += [theme for theme in themes if theme.UID() not in uids]

        return result

    def backReferences(self, portal_type=None, relatesTo='relatesTo'):
        backs = self.context.getBRefs(relatesTo)
        refs = self._checkPermissions(backs)
        mylangrefs = self._filterByLanguage(refs)
        if portal_type != None:
            return [i for i in mylangrefs if i.portal_type == portal_type]
        return mylangrefs

    def forwardReferences(self, portal_type=None):
        forwards = self.context.getRelatedItems()
        refs = self._checkPermissions(forwards)
        mylangrefs = self._filterByLanguage(refs)
        if portal_type != None:
            return [i for i in mylangrefs if i.portal_type == portal_type]
        return mylangrefs

    def autoContextReferences(self, portal_type=None):
        refs = IRelations(self.context).backReferences(portal_type)
        for i in refs:
            refs += IRelations(i).forwardReferences(portal_type)
        uids = []
        ret = []
        for i in refs:
            if (i.UID() not in uids) and (i.UID() != self.context.UID()):
                uids.append(i.UID())
                ret.append(i)
        return ret

    def references(self):
        backs = self.backReferences()
        forwards = self.forwardReferences()

        # make sure we don't get duplicates
        result = backs
        uids = [ref.UID() for ref in result]
        result += [ref3 for ref3 in forwards if ref3.UID() not in uids]

        return result

    def getItems(self, portal_type=None, getBrains=False,
                considerDeprecated=True, constraints=None, theme=None):
        catalog = getToolByName(self.context, 'portal_catalog')

        query = { 'sort_on': 'effective',
                  'sort_order': 'reverse',
                  'Language': self.context.getLanguage(),
                  'effectiveRange': DateTime() }

        if theme != None:
            if considerDeprecated:
                contextThemes = theme.nondeprecated_tags
            else:
                contextThemes = theme.tags
            query['getThemes'] = contextThemes

        if constraints:
            query.update(constraints)

        if portal_type != None:
            # Highlights and Press releases are usually listed together
            if portal_type in ['Highlight', 'PressRelease']:
                portal_type = ['Highlight', 'PressRelease']

            elif portal_type == 'File' and IVideoEnhanced.providedBy(self.context):
                query['object_provides'] = 'p4a.video.interfaces.IVideoEnhanced'

            query['portal_type'] = portal_type

        brains = catalog.searchResults(query)

        contextPath = '/'.join(self.context.getPhysicalPath())

        if getBrains:
            return [brain for brain in brains if brain.getPath() != contextPath]
        else:
            return [brain.getObject() for brain in brains if brain.getPath() != contextPath]

    def byTheme(self, portal_type=None, getBrains=False,
                considerDeprecated=True, constraints=None):
        theme = queryAdapter(self.context, IThemeTagging)
        if theme is None:
            # not theme taggable
            return []
        return self.getItems(portal_type, getBrains, considerDeprecated,
                             constraints, theme)

    def byPublicationGroup(self, samePortalType=True, getBrains=False,
                           constraints=None):
        context = self.context
        if not hasattr(context, 'getPublication_groups'):
            return []

        catalog = getToolByName(context, 'portal_catalog')

        query = { 'sort_on': 'effective',
                  'sort_order': 'reverse',
                  'Language': context.getLanguage(),
                  'effectiveRange': DateTime() }

        if constraints:
            query.update(constraints)

        if samePortalType:
            # Highlights and Press releases are usually listed together
            portal_type = context.portal_type
            if portal_type in ['Highlight', 'PressRelease']:
                portal_type = ['Highlight', 'PressRelease']

            query['portal_type'] = portal_type

        brains = catalog.searchResults(query)

        contextPath = '/'.join(context.getPhysicalPath())

        if getBrains:
            return [brain for brain in brains if brain.getPath() != contextPath]
        else:
            return [brain.getObject() for brain in brains if brain.getPath() != contextPath]


    def _checkPermissions(self, references):
        result = []
        mtool = getToolByName(self.context, 'portal_membership')

        for i in range(len(references)):
            try:
                obj = references[i]
            except Unauthorized:
                continue
            if obj not in result:
                if mtool.checkPermission('View', obj):
                    result.append(obj)

        return result



    def _filterByLanguage(self, references):
        result = []
        lang = self.context.getLanguage()

        for i in range(len(references)):
            try:
                obj = references[i]
            except Unauthorized:
                continue
            if obj not in result:
                if obj.getLanguage() == lang:
                    result.append(obj)

        return result

