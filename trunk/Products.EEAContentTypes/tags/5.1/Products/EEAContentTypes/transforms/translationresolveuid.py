""" Resolve UID
"""
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import ITransform
from Products.kupu.plone.config import UID_PATTERN
from zope.interface import implements


class TranslationResolveUid:
    """ Resolves uid in resolveuid/UID links and tries to get the translation.
    """

    implements(ITransform)

    __name__ = "translation_resolveuid"
    inputs   = ('text/html',)
    output = "text/html"

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs' : ('list', 'Inputs',
                        'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name


    def name(self):
        """ Name
        """
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def resolveuid(self, context, reference_catalog, uid):
        """Convert a uid to an object by looking it up in the reference catalog.
        If not found then tries to fallback to a possible hook (e.g.
        so you could resolve uids on another system).
        """
        target = reference_catalog.lookupObject(uid)
        if target is not None:
            if hasattr(target, 'getTranslation'):
                lang = context.REQUEST.get('LANGUAGE', None)
                if lang is not None:
                    target = target.getTranslation(lang) or target
            return target
        hook = getattr(context, 'kupu_resolveuid_hook', None)
        if hook is not None:
            target = hook(uid)

        return target



    def convert(self, orig, data, **kwargs):
        """ Convert
        """
        context = kwargs.get('context', None)
        if context is not None:
            rc = getToolByName(context, 'reference_catalog')

            def replaceUids(match):
                """ Replace UIDs
                """
                tag = match.group('tag')
                uid = match.group('uid')
                target = self.resolveuid(context, rc, uid)
                if target is not None:
                    #is_empty = False

                    #WIP: this code is commented, is_empty is no longer used
                    #if (hasattr(target, 'isCanonical') and
                        #not target.isCanonical()):
                        #cat = getToolByName(context, 'portal_catalog')
                        #rid = cat.getrid('/'.join(target.getPhysicalPath()))
                        #metadata = cat.getMetadataForRID(rid)
                        #if metadata and metadata.get('is_empty', False):
                            #return (tag + target.absolute_url_path() +
                                    #'/not_available_lang')
                    try:
                        url = target.getRemoteUrl()
                    except AttributeError:
                        url = target.absolute_url_path()

                    return tag + url

                return match.group(0)

            html = UID_PATTERN.sub(replaceUids, orig)

            data.setData(html)
        return data

def register():
    """ Register
    """
    return TranslationResolveUid()
