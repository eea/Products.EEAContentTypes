""" Relations
"""
from AccessControl import Unauthorized

from zope.component import adapts, queryAdapter
from zope.interface import implements, Interface
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.interfaces import IRelations
from eea.themecentre.interfaces import IThemeTagging
from eea.mediacentre.interfaces import IVideo


class Relations(object):
    """ Relations
    """
    implements(IRelations)
    adapts(Interface)

    def __init__(self, context):
        self.context = context

    def all(self, portal_type=None, constraints=None):
        """ All
        """
        forwards = self.forwardReferences()
        backs = self.backReferences()
        themes = self.byTheme(portal_type=portal_type,
                              constraints=constraints)

        result = forwards

        # filter the results to only return unique results
        uids = [ref.UID() for ref in result]
        result += [back for back in backs if back.UID() not in uids]
        uids = [ref2.UID() for ref2 in result]
        result += [theme for theme in themes if theme.UID() not in uids]

        return result

    def backReferences(self, portal_type=None, relatesTo='relatesTo'):
        """ Back
        """
        backs = self.context.getBRefs(relatesTo)
        refs = self._checkPermissions(backs)
        mylangrefs = self._filterByLanguage(refs)
        if portal_type != None:
            return [i for i in mylangrefs if i.portal_type == portal_type]
        return mylangrefs

    def forwardReferences(self, portal_type=None):
        """ Forward
        """
        forwards = self.context.getRelatedItems()
        refs = self._checkPermissions(forwards)
        mylangrefs = self._filterByLanguage(refs)
        if portal_type != None:
            return [i for i in mylangrefs if i.portal_type == portal_type]
        return mylangrefs

    def autoContextReferences(self, portal_type=None):
        """ Auto
        """
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
        """ References
        """
        backs = self.backReferences()
        forwards = self.forwardReferences()

        # make sure we don't get duplicates
        result = backs
        uids = [ref.UID() for ref in result]
        result += [ref3 for ref3 in forwards if ref3.UID() not in uids]

        return result

    def getItems(self, portal_type=None, getBrains=False,
                 considerDeprecated=True, constraints=None, theme=None):
        """ Items
        """
        catalog = getToolByName(self.context, 'portal_catalog')

        query = {'sort_on': 'effective',
                 'sort_order': 'reverse',
                 'effectiveRange': DateTime()}
        if getattr(self.context, 'getLanguage', None):
            query['Language'] = self.context.getLanguage()

        if theme:
            if considerDeprecated:
                # 13986 ExternalDataSpec Theme doesn't have nondepregated_tags
                contextThemes = getattr(theme, 'nondeprecated_tags', None)
                if not contextThemes:
                    contextThemes = theme.tags
            else:
                contextThemes = theme.tags
            query['getThemes'] = contextThemes

        queryThemesSeparately = False
        if constraints:
            # add 1 more to limit since we might get contextPath as result
            if constraints.get('sort_limit'):
                constraints['sort_limit'] += 1
            if constraints.get('queryThemesSeparately'):
                queryThemesSeparately = True
            query.update(constraints)

        if portal_type:
            # Highlights and Press releases are usually listed together
            if portal_type in ['Highlight', 'PressRelease']:
                portal_type = ['Highlight', 'PressRelease']

            elif (portal_type == 'File' and
                      IVideo.providedBy(self.context)):
                query['object_provides'] = 'eea.mediacentre.interfaces.IVideo'

            query['portal_type'] = portal_type

        res = []
        # split getThemes query only if we have the queryThemesSeparately flag
        # enabled
        if theme and queryThemesSeparately:
            for item in contextThemes:
                query['getThemes'] = item
                res.extend(catalog.searchResults(query))
            brains = res
        else:
            brains = catalog.searchResults(query)
        contextPath = '/'.join(self.context.getPhysicalPath())
        if getBrains:
            return [brain for brain in brains if brain.getPath() != contextPath]
        else:
            return [brain.getObject() for
                    brain in brains if brain.getPath() != contextPath]

    def byTheme(self, portal_type=None, getBrains=False,
                considerDeprecated=True, constraints=None):
        """ By theme
        """
        theme = queryAdapter(self.context, IThemeTagging)
        if theme is None:
            # not theme taggable
            return []
        return self.getItems(portal_type, getBrains, considerDeprecated,
                             constraints, theme)

    def byPublicationGroup(self, samePortalType=True, getBrains=False,
                           constraints=None):
        """ By publication group
        """
        context = self.context
        if not hasattr(context, 'getPublication_groups'):
            return []

        catalog = getToolByName(context, 'portal_catalog')

        query = {'sort_on': 'effective',
                 'sort_order': 'reverse',
                 'Language': context.getLanguage(),
                 'effectiveRange': DateTime()}

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
            return [brain.getObject() for
                    brain in brains if brain.getPath() != contextPath]

    def _checkPermissions(self, references):
        """ Check permissions
        """
        result = []
        mtool = getToolByName(self.context, 'portal_membership')

        for i, _item in enumerate(references):
            try:
                obj = references[i]
            except Unauthorized:
                continue
            if obj not in result:
                if mtool.checkPermission('View', obj):
                    result.append(obj)

        return result

    def _filterByLanguage(self, references):
        """ Filter by language
        """
        result = []
        try:
            lang = self.context.getLanguage()
        except Exception:
            return result

        for i, _item in enumerate(references):
            try:
                obj = references[i]
            except Unauthorized:
                continue
            if obj not in result:
                try:
                    if obj.getLanguage() == lang:
                        result.append(obj)
                except Exception:
                    continue

        return result
