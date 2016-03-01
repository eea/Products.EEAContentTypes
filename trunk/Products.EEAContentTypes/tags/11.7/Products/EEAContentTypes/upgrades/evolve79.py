""" Evolve 79 profile
"""
from Products.CMFCore.utils import getToolByName
from Products.ATVocabularyManager.utils.vocabs import createSimpleVocabs
from zope.component.hooks import getSite

from Products.EEAContentTypes.vocabulary import VOCABULARIES


def evolve(context):
    """creates/imports the atvm vocabs."""

    site = getSite()
    atvm = getToolByName(site, 'portal_vocabularies')
    createSimpleVocabs(atvm, VOCABULARIES)
