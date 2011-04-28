# -*- coding: utf-8 -*-
#
# File: migrateHighlights.py
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

from Products.EEAContentTypes.setup.vocabularies import *
from Products.ATContentTypes.config import MX_TIDY_OPTIONS
from Products.ATContentTypes.config import HAS_MX_TIDY
from Products.CMFCore.utils import getToolByName

from htmlentitydefs import name2codepoint

import re
import chardet

if HAS_MX_TIDY:
    from mx.Tidy import tidy as mx_tidy


encodings = {}
decoding_errors = {}
encoding_errors = {}
escaping_errors = {}

errors = {'decoding_errors':decoding_errors,
          'encoding_errors':encoding_errors,
          'escaping_errors':escaping_errors,}

def getErrors():
    return errors

def getEncodings():
    return encodings

def returnErrors(err):
    errors = err
    
def safe_unicode(obj, *args):
    """ return the unicode representation of obj """
    try:
        result = unicode(obj, *args)
    except UnicodeDecodeError:
        # obj is byte string
        ascii_text = str(obj).encode('string_escape')
        result = unicode(ascii_text)

    return result

def getContentTypes(objects, type):
    ''' Find a certain number of types in a list of objects and return '''

    return [obj for obj in objects if obj.meta_type == type]


def stripDTML(data):
    
    tags = ('<dtml-var standard_html_footer>',
            '<dtml-var standard_html_header>',
            '<dtml-var standard_html_header="">',
            '<dtml-var standard_html_footer="">',
            '</dtml-var>',
            '<dtml-var title_or_id="">',
            '<dtml-var "pr_footer_info.contact_info">',)
    
    for tag in tags:
        data = data.replace(tag, '')
        
    return data


def migrateURL(src):
    """ Changes the old EEA domain to the new """

    hits = src.count('.eu.int')
    if hits > 0:
        print "Found %s URLs to change" % hits
    
    return src.replace('.eu.int', '.europa.eu')
    
    
def sniffThemes(src):
    """ Looks for themes in data and returns max 3 """
    
    themes = [theme_keys[0] for theme_keys in vocabs['themes']]
    hits = []
    src = src.lower()
    
    for theme in themes:
        theme.replace('_', ' ')        
        hit = src.count(theme)
        if hit > 0:
            hits.append((theme, hit))
            
    hits.sort(lambda x,y:cmp(x[1],y[1]))

    results = [x[0].replace(' ', '_') for x in hits]    
    if len(results) > 3:
        results = results[:2]

    print "THEMES: %s" % results
    
    return results


def miniTidy(src):
    """ tiny tidy for tidying without all of AT """
    
    if not HAS_MX_TIDY:
        return src

    print "Tidying up"
    result = mx_tidy(src, **MX_TIDY_OPTIONS)
    errors, nwarnings, outputdata, errordata = result
    
    if errors:
        print "Validation Failed: \n %s" % errordata
        return src
        
    return outputdata
    

def htmldecode(text):
    """Decode HTML entities in the given text."""

    # This pattern matches a character entity reference (a decimal numeric
    # references, a hexadecimal numeric reference, or a named reference).
    charrefpat = re.compile(r'&(#(\d+|x[\da-fA-F]+)|[\w.:-]+);?')
    
    if type(text) is unicode:
        uchr = unichr
    else:
        uchr = lambda value: value > 255 and unichr(value) or chr(value)
    def entitydecode(match, uchr=uchr):
        entity = match.group(1)
        if entity.startswith('#x'):
            return uchr(int(entity[2:], 16))
        elif entity.startswith('#'):
            return uchr(int(entity[1:]))
        elif entity in name2codepoint:
            return uchr(name2codepoint[entity])
        else:
            return match.group(0)
    return charrefpat.sub(entitydecode, text)
                                

def makeMigratedObject(location, type, values):
    """ builds the migrated object and does workflow """
                                
    location.invokeFactory(type, 
                      id=values['id'],
                      description=values['description'],
                      title=values['title'],
                      teaser=values['teaser'],
                      text=values['text'],
                      visibilityLevel=values['visibilityLevel'],
                      publishDate=values['publishDate'],
                      expirationDate=values['expiry'],
                      author=values['author'],
                      themes=values['themes'],
                      url=values['url'],)

    newobj = location[values['id']]
                                
    return newobj


def publishContent(portal, obj):
    """ push through to published state """

    wft = getToolByName(portal, 'portal_workflow')
    wft.doActionFor(obj, 'send')
    wft.doActionFor(obj, 'publish')
                                

def createHolder(portal, name):
    """ Creates a folder for the migration and deletes an existing one """

    if hasattr(portal, name):
        portal.manage_delObjects(name)
        
    portal.invokeFactory('Folder', name)
    result = portal[name]
                                
    return result


def reencode(obj, data, thing):
    """ guesses the encoding, decodes it, and returns UTF8 """
    
    if data == '' or data == None:
        return data
    
    # ARGH!
    data = data.replace('\x92',"'")
    data = data.replace('\x96',"--")
    data = data.replace('\x84','&quot;')
    data = data.replace('\x93','&quot;')
    
    #data = data.replace('<br/>','<br />')
    try:
        guess = chardet.detect(data)
        enc=guess['encoding']
    except:
        print "XXX Skipping encoding due to recursion problems with this file: %s" % obj.getId()
        return data
    
    iso_force = ['ISO-8859-2', 'ISO-8859-7', 'ISO-8859-8','IBM855']
    win_force = ['windows-1255','windows-1253']
    cyr_force = ['MacCyrillic','windows-1251','windows-1252']
    
    try:
        objid = obj.id()
    except:
        objid = obj.id
    
    if enc in iso_force:
        
        msg = ">>> Forcing %s encoding of %s from %s to ISO-8859-15" % (thing, objid, enc)
        enc = 'ISO-8859-15'
    elif enc in win_force:
        
        msg = ">>> Forcing %s encoding of %s from %s to windows-1250" % (thing, objid, enc)
        enc = 'windows-1250'
        
    elif enc in cyr_force:
        
        msg = ">>> Forcing %s encoding of %s from %s to ISO-8859-1" % (thing, objid, enc)
        enc = 'ISO-8859-1'    
        
    else:
        
        msg = ">>> Decoding %s's %s from %s with confidence of %s" % (objid, thing, enc, guess['confidence'])
    
    if enc not in ['windows-1250','ISO-8859-15','ascii']:
        print msg
    
    encodings[enc] = None
    
    try:
        decoded = data.decode(enc)
    except Exception, e:
        print "ERROR: Cannot decode %s of %s! %s" % (thing, objid, e)
        decoded = "Decoding error"
        errors['decoding_errors'][objid] = (e, "228")

    if data.count('&') > 0:
        try:
            decoded = htmldecode(decoded)
            #print "Decoding HTML entities"
        except Exception, e:
            errors['escaping_errors'][objid] = (e, "235")
            print "ERROR: Can't unescape HTML entities due to encoding error: %s" % e
            
    try:
        result = decoded.encode('utf-8')
    except Exception, e:
        print "ERROR: Cannot encode %s! %s" % (thing, e)
        errors['encoding_errors'][objid] = (e, "242")
        return None

    return result


def keepTally(root):

    tally = {}
    return findContents(root, tally)


def findContents(root, tally):
        
    objs = root.objectValues()
                                
    for obj in objs:     
        tally[obj.absolute_url()] = {'id':obj.getId(), 
                                     'modified':obj.bobobase_modification_time(), 
                                     'type':obj.meta_type, 
                                     'status':'unmigrated'}
        if obj.isPrincipiaFolderish:
            findContents(obj, tally)

    return tally


def updateTally(tally, obj, status):
                                
    tally[obj.absolute_url()]['status'] = status
    return tally
                                        