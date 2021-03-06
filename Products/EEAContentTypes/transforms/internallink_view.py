""" Internal links
"""
import re
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements

TAG_RE = re.compile(
    r'(<a\s*[^>]*class\s*=\s*"[^>]*[internal|external]-link[^"]*"[^>]*>.*?</a>)')
HREF_RE = re.compile(r'''(<a[^>]*href\s*=\s*")([^"]*)("[^>]*>.*?</a>)''')


class InternalLinkView(object):
    """Simple transform which appends internal links with /view for typesUseViewActionInListings
    """

    implements(ITransform)

    __name__ = "internallink_view"
    inputs = ('text/x-html-safe',)
    output = "text/x-html-safe"

    def __init__(self, name=None):
        self.config_metadata = {
            'inputs': ('list', 'Inputs',
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
        portal_url = '/'.join(getToolByName(
            context, 'portal_url').getPortalObject().getPhysicalPath())
        absolute_url = context.absolute_url()

        if portal_url not in absolute_url and context.Language() == 'en':
            portal_url += '/SITE'

        for tag in TAG_RE.findall(orig):
            for begin, url, end in HREF_RE.findall(tag):
                if url.endswith('/view'):
                    continue

                path = url
                if not url.startswith(portal_url) and url.startswith('/'):
                    path = portal_url + url
                full_portal_url = context.portal_url()
                #96175 remove portal_url from path as catalog expects an
                # absolute url from the catalog path
                res = []
                if full_portal_url in path:
                    path = portal_url + path.replace(full_portal_url, "")
                    res = catalog.searchResults(
                        path={
                            'query': path,
                            'depth': 0
                        },
                        portal_type=use_view_action)

                if len(res):
                    orig = orig.replace(tag, begin + url + '/view' + end)
        data.setData(orig)
        return data


def register():
    """ Register
    """
    return InternalLinkView()


