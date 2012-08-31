""" Base TestCase for EEAContentTypes"""

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase.setup import default_user, default_password
from Testing import ZopeTestCase as ztc
from Testing.testbrowser import Browser
from plone.protect.authenticator import AuthenticatorView
from re import match


PRODUCTS = [
        'kupu',
        'ATVocabularyManager',
        'EEAContentTypes',
        ##'valentine.linguaflow', 'eea.imagescales', 'LinguaPlone',
        'EEAPloneAdmin'
]

for product in PRODUCTS:
    ztc.installProduct(product)

#ztc.installPackage('eea.reports')

@onsetup
def setup_eeacontenttypes():
    """ Set up
    """

    #installs fixture profile

    fiveconfigure.debug_mode = True

    import Products.EEAContentTypes
    zcml.load_config("dependencies.zcml", Products.EEAContentTypes)
    zcml.load_config("testing.zcml", Products.EEAContentTypes.tests)
    zcml.load_config("overrides.zcml", Products.EEAContentTypes)

    #import eea.indicators
    #zcml.load_config("configure.zcml", eea.indicators)
    ztc.installPackage('eea.relations')
    fiveconfigure.debug_mode = False


setup_eeacontenttypes()

PROFILES = [
    'Products.ATVocabularyManager:default',
    'eea.themecentre:default',
    'Products.EEAContentTypes:default',
    'Products.EEAContentTypes.tests:testfixture',
    'eea.relations:default',
]

OPTIONAL_DEPENDENCIES = {
        #key - packagename: value - gs profile name,
        'eea.soer':'eea.soer:default',
        'eea.dataservice':'eea.dataservice:default',
        'eea.reports':'eea.reports:default',
        'eea.indicators':'eea.indicators:default',
        'Products.RedirectionTool':'Products.RedirectionTool:default',
        'Products.EEAPloneAdmin':'Products.EEAPloneAdmin:default',
        'valentine.linguaflow':'valentine.linguaflow:default',
    }

for pkg, gs in OPTIONAL_DEPENDENCIES.items():
    try:
        __import__(pkg)
    except ImportError, err:
        pass
    else:
        PROFILES.insert(0, gs)

PloneTestCase.setupPloneSite(products=PRODUCTS, extension_profiles=PROFILES)


class EEAContentTypeTestCase(PloneTestCase.PloneTestCase):
    """Base TestCase for EEAContentTypes."""

    def setRequestMethod(self, method):
        """ Request method
        """
        self.app.REQUEST.set('REQUEST_METHOD', method)
        self.app.REQUEST.method = method

    def getAuthenticator(self):
        """ Authenticator getter
        """
        tag = AuthenticatorView('context', 'request').authenticator()
        pattern = '<input .*name="(\w+)".*value="(\w+)"'
        return match(pattern, tag).groups()

    def setupAuthenticator(self):
        """ Authenticator setter
        """
        name, token = self.getAuthenticator()
        self.app.REQUEST.form[name] = token


class EEAContentTypeFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional TestCase"""

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            user = default_user
            pwd = default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % (user, pwd))
        return browser
