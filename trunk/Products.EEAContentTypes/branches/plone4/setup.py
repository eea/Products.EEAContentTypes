from setuptools import setup, find_packages
import os
from os.path import join

name = 'Products.EEAContentTypes'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name=name,
      version=version,
      description="EEA logic and content types",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='eea',
      author='European Environment Agency (EEA)',
      author_email='webadmin@eea.europa.eu',
      url='http://svn.eionet.europa.eu/projects/Zope',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.monkeypatcher',
          # -*- Extra requirements: -*-

          'Products.LinguaPlone',
          'Products.ATVocabularyManager',
          'Products.OrderableReferenceField',
          'Products.fatsyndication',
          'Products.basesyndication',
          'Products.RedirectionTool',

          'eea.rdfmarshaller',
          'eea.facetednavigation',
          'eea.rdfrepository',
          'eea.themecentre',
          'eea.translations',
          'eea.promotion',
          'Products.EEAPloneAdmin',
          'Products.NavigationManager',

          'valentine.imagescales',
          'bda.feed',
          'p4a.video',
          'rdflib',
          'eea.promotion',

          #required in tests
          'eea.testcase',
          'valentine.linguaflow',
          'eea.reports',
          'eea.design',

          #TODO: enable when plone4 migration
          #'eea.dataservice',
          #'eea.locationwidget',
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
