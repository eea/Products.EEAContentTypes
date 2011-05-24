""" Base TestCase for EEAContentTypes"""
from plone.app.blob.tests import db
db ## pyflakes, this import is needed for tests
from Products.PloneTestCase import PloneTestCase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.GenericSetup import EXTENSION, profile_registry

PRODUCTS = [
    'CacheSetup', 'PlonePAS', 'FiveSite',
    'ATVocabularyManager', 'EEAContentTypes',
    'valentine.linguaflow', 'valentine.imagescales', 'LinguaPlone',
    'RichTopic', 'ThemeCentre', 'kupu', 'PloneLanguageTool',
    'EEAPloneAdmin'
]

try:
    from Products import RedirectionTool
except ImportError, err:
    # RedirectionTool not present
    pass
else:
    RedirectionTool #pyflakes, #pylint: disable-msg=W0104
    PRODUCTS.append('RedirectionTool')

profile_registry.registerProfile(
                    'testfixture',
                    'test:EEAContentTypes',
                    'Extension profile for testing EEAContentTypes',
                    'profile/testfixture',
                    'EEAContentTypes',
                    EXTENSION,
                    for_=IPloneSiteRoot)

@onsetup
def setup_eeacontenttypes():
    """ Set up
    """
    fiveconfigure.debug_mode = True
    import Products.Five
    import Products.FiveSite
    import Products.CMFSquidTool
    zcml.load_config('meta.zcml', Products.Five)
    zcml.load_config('configure.zcml', Products.FiveSite)
    zcml.load_config('configure.zcml', Products.CMFSquidTool)
    fiveconfigure.debug_mode = False

    PloneTestCase.installProduct('Five')
    PloneTestCase.installProduct('CMFSquidTool')
    PloneTestCase.installProduct('PlonePAS')
    for product in PRODUCTS:
        PloneTestCase.installProduct(product)

setup_eeacontenttypes()

# Try to install eea.indicators content-types
try:
    from eea import indicators
except ImportError, err:
    # eea.indicators not present
    pass
else:
    indicators #pyflakes, #pylint: disable-msg=W0104
    PRODUCTS.append('eea.indicators')

PROFILES = [
    'EEAContentTypes:eeacontenttypes',
    'EEAContentTypes:testfixture',
]

# Try to install eea.reports content-types
try:
    from eea import reports
except ImportError, err:
    # eea.reports not present
    pass
else:
    reports #pyflakes, #pylint: disable-msg=W0104
    PROFILES.append('eea.reports:default')

# Try to install eea.dataservice content-types
try:
    from eea import dataservice
except ImportError, err:
    # eea.dataservice not present
    pass
else:
    dataservice #pyflakes, #pylint: disable-msg=W0104
    PROFILES.append('eea.dataservice:default')

# Try to install eea.soer content-types
try:
    from eea import soer
except ImportError, err:
    # eea.soer not present
    pass
else:
    soer #pyflakes, #pylint: disable-msg=W0104
    PROFILES.append('eea.soer:default')

PloneTestCase.setupPloneSite(
    extension_profiles=PROFILES,
    products=PRODUCTS)

class EEAContentTypeTestCase(PloneTestCase.PloneTestCase):
    """Base TestCase for EEAContentTypes."""

class EEAContentTypeFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional TestCase"""
