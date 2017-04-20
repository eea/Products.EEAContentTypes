""" EEA Content Types installer
"""
import os
from setuptools import setup, find_packages

NAME = 'Products.EEAContentTypes'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()

setup(name=NAME,
      version=VERSION,
      description="EEA logic and content types",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Zope2",
          "Framework :: Plone",
          "Framework :: Plone :: 4.0",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "Programming Language :: Zope",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.7",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "License :: OSI Approved :: GNU General Public License (GPL)",
      ],
      keywords='EEA Add-ons Plone Zope',
      author='European Environment Agency: IDM2 A-Team',
      author_email='eea-edw-a-team-alerts@googlegroups.com',
      url="https://github.com/eea/Products.EEAContentTypes",
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
          'Products.RedirectionTool',

          'eea.rdfmarshaller',
          'eea.facetednavigation',
          'eea.forms',
          'eea.mediacentre',
          'eea.themecentre',
          'eea.translations',
          'eea.promotion',
          'eea.vocab',
          'eea.depiction',
          'eea.daviz',
          'Products.EEAPloneAdmin',
          'Products.NavigationManager',

          'rdflib',
          'pika',
          'collective.monkeypatcher',
          'eea.reports',
          'eea.relations',

          'eea.cache',

          #required in tests
          'eea.dataservice',
          'eea.design',
          'eea.geotags',
          'eea.indicators',
          'eea.soer',
          'valentine.linguaflow',
          'eventlet',

          'eea.rabbitmq.client'
          #obsolete
          #'Products.CMFSquidTool',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
