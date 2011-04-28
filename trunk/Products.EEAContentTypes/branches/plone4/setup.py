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

          'Products.basesyndication',
          'bda.feed',
          'p4a.video',
          'rdflib==2.4.2',
          'Products.LinguaPlone',
          'Products.ATVocabularyManager',
          'Products.OrderableReferenceField',

          'eea.rdfmarshaller',

          #TODO: enable when plone4 migration
          #'eea.promotion',
          #'eea.dataservice',
          #'eea.themecentre',
          #'eea.locationwidget',

          #required in tests
          #'eea.design',
          #'eea.testcase',

          #'Products.CMFSquidTool',

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
