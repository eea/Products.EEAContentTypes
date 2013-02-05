""" Internal links
"""
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
import re


TAG_RE = re.compile(
    r'''(<a\s*[^>]*class\s*=\s*"[^>]*internal-link[^"]*"[^>]*>.*?</a>)''')
HREF_RE = re.compile(r'''(<a[^>]*href\s*=\s*")([^"]*)("[^>]*>.*?</a>)''')

class InternalLinkView:
    """Simple transform which replaces all email addresses with a javascript."""

    implements(ITransform)

    __name__ = "internallink_view"
    inputs   = ('text/x-html-safe',)
    output = "text/x-html-safe"

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs' : ('list', 'Inputs',
                        'Input(s) MIME type. Change with care.'),
            }
        if name:
            self.__name__ = name

    def name(self):
        """ Name """
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        """ Convert
        """
        context = kwargs['context']
        catalog = getToolByName(context, 'portal_catalog')
        props = getToolByName(context, 'portal_properties')
        site_props = getattr(props, 'site_properties', None)
        use_view_action = ()
        if site_props:
            use_view_action = site_props.getProperty(
                'typesUseViewActionInListings', ())
        portal_url = '/'.join(getToolByName(context,
                              'portal_url').getPortalObject().getPhysicalPath())
        absolute_url = context.absolute_url()

        if not portal_url in absolute_url and context.Language() == 'en':
            portal_url += '/SITE'

        for tag in TAG_RE.findall(orig):
            for begin, url, end in HREF_RE.findall(tag):
                if url.endswith('/view'):
                    continue

                path = url
                if not url.startswith(portal_url) and  url.startswith('/'):
                    path = portal_url + url

                res = catalog.searchResults(path=path,
                                            portal_type = use_view_action)

                if len(res):
                    orig = orig.replace(tag, begin + url + '/view' + end)
        data.setData(orig)
        return data

def register():
    """ Register
    """
    return InternalLinkView()
