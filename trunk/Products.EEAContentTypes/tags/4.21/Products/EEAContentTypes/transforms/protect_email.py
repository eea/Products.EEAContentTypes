""" Protect email
"""
from Products.EEAContentTypes.browser.organisation import emailjs_dot, emailjs
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
import re

#from Products.CMFDefault.utils import bodyfinder

EMAIL_RE = re.compile(
    r"(?<!mailto:)(?<!>)(?<!\.)\b(?P<name>(?:[a-zA-Z0-9-]+)(?:\.[a-zA-Z0-9-]+)*)@(?P<domain>(?:[a-zA-Z0-9-]+)(?:\.[a-zA-Z0-9-]+)*(?:\.[a-zA-Z]{2,4}))(?P<dot>[\.\"]?)\b")
# `email title <email@domain.com>`__
EMAIL_TITLE = re.compile(r"`([^`]+)(\s+)&lt;(.+)&gt;`__")


class ProtectEmail:
    """Simple transform which replaces all email addresses with a javascript."""

    implements(ITransform)

    __name__ = "protect_email"
    inputs = ('text/x-html-safe',)
    output = "text/x-html-safe"

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

    def convert(self, orig, data, **kwargs):
        """ Convert
        """
        emailsWithTitle = EMAIL_TITLE.findall(orig)
        for title, space, email in emailsWithTitle:
            name, domain = email.split('@')
            js = emailjs % (name, domain, title)
            toReplace = "`%s%s&lt;%s&gt;`__" % (title, space, email)
            orig = orig.replace(toReplace, js)

        emails = EMAIL_RE.findall(orig)
        for name, domain, dot in emails:
            email = '%s@%s' % (name, domain)
            linkName = '%s at %s' % (name, domain)
            js = emailjs_dot % (name, domain, linkName, dot)
            orig = orig.replace(email + dot, js)
        data.setData(orig)
        return data

def register():
    """ Register
    """
    return ProtectEmail()
