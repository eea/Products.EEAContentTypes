""" Base TestCase for EEAContentTypes"""

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.GenericSetup import EXTENSION, profile_registry
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

import sys

#from plone.app.blob.tests import db
#db ## pyflakes, this import is needed for tests

PRODUCTS = [
    'Products.ATVocabularyManager', 
    ###'EEAContentTypes',
    ##'valentine.linguaflow', 'valentine.imagescales', 'LinguaPlone',
    ##'EEAPloneAdmin'
]

for product in PRODUCTS:
    PloneTestCase.installProduct(product)

profile_registry.registerProfile(
                    'testfixture',
                    'test:EEAContentTypes',
                    'Extension profile for testing EEAContentTypes',
                    'profile/testfixture',
                    'Products.EEAContentTypes',
                    EXTENSION,
                    for_=IPloneSiteRoot)


@onsetup
def setup_eeacontenttypes():
    """ Set up
    """
    fiveconfigure.debug_mode = True

    for product in PRODUCTS:
        __import__(product)
        pkg = sys.modules[product]
        zcml.load_config("configure.zcml", pkg)

    fiveconfigure.debug_mode = False


setup_eeacontenttypes()

PROFILES = [
    'Products.EEAContentTypes:default',
    'Products.EEAContentTypes:testfixture',
    #'Products.ATVocabularyManager:default',
]


OPTIONAL_DEPENDENCIES = {
        #key - packagename: value - gs profile name,
        'eea.soer':'eea.soer:default',
        'eea.dataservice':'eea.dataservice:default',
        'eea.reports':'eea.reports:default',
        'eea.indicators':'eea.indicators:default',
        'Products.RedirectionTool':'Products.RedirectionTool:default',
    }

for pkg, gs in OPTIONAL_DEPENDENCIES.items():
    try:
        __import__(pkg)
    except ImportError, err:
        pass
    else:
        PROFILES.append(gs)


PloneTestCase.setupPloneSite(products=PRODUCTS, extension_profiles=PROFILES)


class EEAContentTypeTestCase(PloneTestCase.PloneTestCase):
    """Base TestCase for EEAContentTypes."""

class EEAContentTypeFunctionalTestCase(PloneTestCase.FunctionalTestCase):
    """ Functional TestCase"""
