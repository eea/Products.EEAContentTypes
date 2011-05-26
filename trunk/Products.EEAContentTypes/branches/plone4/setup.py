""" EEA Content Types installer
"""
from setuptools import setup, find_packages
import os

NAME = 'Products.EEAContentTypes'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="EEA logic and content types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
           "Framework :: Plone",
           "Programming Language :: Python",
           "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea',
      author='European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url="https://svn.eionet.europa.eu/projects/"
          "Zope/browser/trunk/Products.EEAContentTypes",
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',

          'Products.LinguaPlone',
          'Products.ATVocabularyManager',
          'Products.OrderableReferenceField',
          'Products.fatsyndication',
          'Products.basesyndication',
          'Products.RedirectionTool',

          'eea.rdfmarshaller',
          'eea.facetednavigation',
          'eea.rdfrepository',
          'eea.locationwidget',
          'eea.mediacentre',
          'eea.themecentre',
          'eea.translations',
          'eea.promotion',
          'eea.vocab',
          'valentine.imagescales',
          'Products.EEAPloneAdmin',
          'Products.NavigationManager',

          'bda.feed',
          'p4a.video',
          'rdflib',
          'collective.monkeypatcher',
          'eea.reports',

          #required in tests
          'valentine.linguaflow',
          'eea.testcase',
          'eea.design',

          'hachoir-core',   #only for the patch

          #TODO: enable when plone4 migration
          #'eea.dataservice',
          #'eea.geotags',
          #'eea.mediacentre',

          #required in tests
          #'eea.indicators',
          #'eea.soer',

          #obsolete
          #'Products.CMFSquidTool',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
