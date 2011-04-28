#!/usr/local/bin/python
# -*- coding: utf-8 -*-

#
# File: migrateNewsReleases.py
#
# Copyright (c) 2006 by Tom 'Spanky' Kapanka
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """ Spanky """
__docformat__ = 'plaintext'

from Products.EEAContentTypes.Extensions.migrationUtils import *
from Products.EEAContentTypes.Extensions.movingDay import pack
from Products.EEAContentTypes.content import PressRelease
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

languages = {}
all_dtml = {}

visibilityLevel = "middle"
    
def migrate(self):

    portal = getToolByName(self,'portal_url').getPortalObject()
    root = portal['newsreleases']

    #place for new ones
    folder = createHolder(portal, 'ATPressReleases')

    #old ones
    legacy = getContentTypes(root.objectValues(), 'DTML Document')
    
    tally = keepTally(root)
    
    translations, tally = migrateEnglish(portal, legacy, folder, tally)

    tally = makeTranslations(legacy, translations, folder, tally)
    
    addLanguages(portal)

    errors = getErrors()
    encodings = getEncodings()

    print "Encountered the following encodings: %s" % encodings.keys()
    print
    from pprint import pprint as pp
    print "Encountered the following DECODING errors:"
    pp(errors['decoding_errors'])
    print
    print "Encountered the following ENCODING errors:"
    pp(errors['encoding_errors'])
    print
    print "Encountered the following ESCAPING errors:"
    pp(errors['escaping_errors'])
    print
    print "The following objects were missed:"
    missed = [x for x in all_dtml.keys() if all_dtml[x] == 0]
    pp(missed)
    
    print "Migrating the rest"
    tally = pack(root.objectValues(), folder, tally=tally)
    
    for k,v in tally.iteritems():
        if v['status'] == 'unmigrated':
            print k
            print v    
    
    print "Done diddly-un!"
    
    
def migrateEnglish(portal, legacy, folder, tally):
    """ Migrates EN files & html files, build EN list to translate """

    translations = []

    for obj in legacy:

        id = obj.id()
        all_dtml[id] = 0

        if id[-3:] == "-en":
            print
            print "+ Adding %s to files to be translated" % id
            translations.append(obj)
            
        else:
        
            if (id[-3:] != '-en' and id[-4:] != 'html' and id[-3:] != "htm"):
                
                if id[-3:-2] != '-' and id[-4:] != 'html' and id[-3:] != "htm":
                    # english with no -en extension
                    print "+ Adding %s to files to be translated" % id
                    translations.append(obj)
                else:
                
                    print "  Skipping file: %s" % id
                    continue
        
        print
        print "Migrating %s ... " % id
        
        results = getMigrationContent(obj)

        all_dtml[results['id']] = 1
        
        # yank "en" suffix for default obj
        if results['id'][-3:] == '-en':
            results['id'] = results['id'][:-3]

        #make it
        try:
            new = makeMigratedObject(folder, 'PressRelease', results)
            tally = updateTally(tally, obj, 'migrated')
            publishContent(portal, new)
        except:
            print "XXX Did not make migrated object"
            #import pdb; pdb.set_trace()
            pass
        
    return translations, tally


def makeTranslations(legacy, translations, folder, tally):
    # Add translations for languages
    for obj in translations:

        # find other languages for each English one
        root_name = obj.id()[:-3]
        
        # Some english ones have no extension...joy!
        if obj.id()[-3:] != "-en":
            root_name = obj.id()
            
        for item in legacy:

            id = item.id()
            lang = id[-2:]
            
            if id[:-3] == root_name and lang != 'en':

                languages[lang] = None
                results = getMigrationContent(item)
                
                # let LinguaPlone make the ID
                del results['id']
                if results['themes'] == []:
                    del results['themes']
                
                # get the object to translate
                en_obj = folder[root_name]
                
                print "Translating %s into %s" % (en_obj.id, lang)
                
                try:
                    
                    en_obj.addTranslation(lang, **results)
                    all_dtml[id] = 1
                    tally = updateTally(tally, item, 'migrated')
                    
                except Exception, e:
                    
                    errors = getErrors()
                    error = "ERROR! Cannot write object (encoding problem?) %s" % e
                    errors['encoding_errors'][obj.id()] = (error, "126")
                    returnErrors(errors)
                    print error
                
                print
                print ":================================:"
                print
    return tally
    

def addLanguages(portal):
    """ Add languages to LinguaPlone """

    lang_tool = getToolByName(portal, 'portal_languages')
    lang_tool.setDefaultLanguage('en')
    lang_tool.start_neutral = 0
    
    langs = languages.keys()
    print
    print "Installing languages: %s" % langs
    
    avail_langs = lang_tool.getAvailableLanguages()
    
    for lang in langs:
        if lang in avail_langs.keys():
            print "+Adding language: %s" % lang
            lang_tool.addSupportedLanguage(lang)
        else:
            print "XXX: Language code not supported: %s" % lang

def getMigrationContent(obj):
    """ gets content from an object to be migrated """

    body = obj.read()
    body = reencode(obj, body, "body")
    body = stripDTML(body)
    body = migrateURL(body)
    title = reencode(obj, obj.title or obj.id(), "title")
    teaser = hasattr(obj, 'teaser') and obj.teaser or None
    if teaser:
        teaser = reencode(obj, teaser, "teaser")
    themes = sniffThemes(title + str(teaser))
    
    results = {}

    # gather everything up
    results['id'] = obj.id()
    results['description'] = teaser    
    results['title'] =  title
    results['teaser'] = teaser
    results['text'] = miniTidy(body)
    results['visibilityLevel'] = visibilityLevel  
    results['publishDate'] = hasattr(obj, 'releasedate') and obj.releasedate or DateTime('01/01/1972')
    results['expiry'] = results['publishDate'] + 7
    results['author'] = obj.author or None
    results['themes'] = themes    
    results['url'] = ''

    return(results)
