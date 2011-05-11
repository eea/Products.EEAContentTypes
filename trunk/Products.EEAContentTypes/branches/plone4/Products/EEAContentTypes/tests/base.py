""" Base TestCase for EEAContentTypes"""

from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.GenericSetup import EXTENSION, profile_registry
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Testing import ZopeTestCase as ztc

import sys

#from plone.app.blob.tests import db
#db ## pyflakes, this import is needed for tests



PRODUCTS = [
    'ATVocabularyManager', 
    'EEAContentTypes',
    ##'valentine.linguaflow', 'valentine.imagescales', 'LinguaPlone',
    ##'EEAPloneAdmin'
]

for product in PRODUCTS:
    ztc.installProduct(product)

@onsetup
def setup_eeacontenttypes():
    """ Set up
    """
    fiveconfigure.debug_mode = True

    #for product in PRODUCTS:
        #__import__(product)
        #pkg = sys.modules[product]
        #zcml.load_config("configure.zcml", pkg)

    fiveconfigure.debug_mode = False
    profile_registry.registerProfile(
                        name='testfixture',
                        title='EEAContentTypes test fixtures',
                        description='Extension profile for testing EEAContentTypes',
                        path='profile/testfixture',
                        product='Products.EEAContentTypes',
                        profile_type=EXTENSION,
                        for_=IPloneSiteRoot
                    )


setup_eeacontenttypes()

PROFILES = [
    'Products.ATVocabularyManager:default',
    'Products.EEAContentTypes:default',
    'Products.EEAContentTypes:testfixture',
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
