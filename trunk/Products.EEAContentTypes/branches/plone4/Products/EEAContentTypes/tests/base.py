""" Base TestCase for EEAContentTypes"""

from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc


PRODUCTS = [
        'kupu',
        'ATVocabularyManager', 
        'EEAContentTypes',
        ##'valentine.linguaflow', 'valentine.imagescales', 'LinguaPlone',
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
    import Products.EEAContentTypes.tests
    zcml.load_config("testing.zcml", Products.EEAContentTypes.tests)
    fiveconfigure.debug_mode = False


setup_eeacontenttypes()

PROFILES = [
    'Products.ATVocabularyManager:default',
    'eea.themecentre:default',
    'Products.EEAContentTypes:default',
    'Products.EEAContentTypes.tests:testfixture',
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


class EEAContentTypeFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional TestCase"""

