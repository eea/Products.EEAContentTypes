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

__author__ = """ Spanky """
__docformat__ = 'plaintext'

"""
Moving Day is here again...moving day!
        -- Riptopolis
        
The idea behind this script is that you have a bunch of content in
Zope, and you want it to be ATCT in your shiny new Plone site.

Take the content and export to a .zexp file.  Import that into
your Plone site and point "ROOT" (in floorplan) at that location.

I use the metaphor of moving to a new apartment throughout, so
naming things is easier.  Movin' on up, to the East Side!

"""

from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.Extensions.floorplan import *
import re
from pprint import pprint as pp
from types import StringType

def moveOut(self):
    """ Finds types from 'root' and migrates them to AT Content Types. """

    portal = getToolByName(self,'portal_url').getPortalObject()    

    if CREATE_DEST:
        new_apartment = signLease(portal, DESTINATION)
    else:
        new_apartment = portal[DESTINATION]
        
    old_apartment = portal[ROOT]
    furniture = old_apartment.objectValues()
    
    print  "\nCall all your friends! It's moving day!\n"
    
    pack(furniture, new_apartment)
    
    print  "\nDone!"


def pack(furniture, location, tally={}):
    """ make an inventory of your current things """

    print "Packing furniture:"
    for item in furniture:
        try:
            folderish = item.isPrincipiaFolderish
        except:
            print "Cannot determine folderish nature of %s" % item
            folderish = False
            
        if folderish:
            
            print "\n>>>Emptying drawers of %s" % item.getId()
            # make folder and descend into it
            folder, tally = move(item, location, tally)
            furniture = item.objectValues()
            tally = pack(furniture, folder, tally)
        
        else:
            
            newobj, tally = move(item, location, tally)
            
    return tally
            
    
def move(item, location, tally):
    """ Moves the furniture to the new place. """
    
    type = item.meta_type
    
    if type in TYPES.keys():
      
        # start with the basics
        id = item.getId()
        
        if id == 'CONTACT975679915':
            import pdb; pdb.set_trace()
        
        print "Moving %s" % id
        
        title = translate(item.title_or_id())
        
        newid = location.invokeFactory(TYPES[type],
                                          id=id,
                                          title=title,)
        newobj = location[newid]
        
        # set desired attributes from one to the other
        if FIELDMAP.has_key(type):
            for attr_from,attr_to in FIELDMAP[type].iteritems():

                if attr_from == 'method':      
                    for method_name,attr in attr_to.iteritems():
                        mutator = getattr(newobj, attr)
                        method = getattr(item, method_name)
                        
                        try:
                            value = method.__call__()
                        except:
                            value = method.__call__(item)
                            
                        if type == "DTML Document":
                            if STRIP_DTML:
                                value = stripDTMLs(item.absolute_url(), value)
                            if REMOVE_ALL_DTML:
                                value = removeAllDTML(item.absolute_url(), value)
                            if RENDER_DTML:
                                value = renderDTML
                        mutator(value)
                else:
                    mutator = getattr(newobj, attr_to)
                    value = getattr(item, attr_from)
                    
                    if isinstance(value, StringType) and type not in ['Image','File']:
                        try:
                            value.decode('utf8')
                        except:
                            value = translate(value)
                    
                    mutator(value)
                    
        if tally:
            tally = updateTally(tally, item, 'migrated')
            
        return newobj, tally
    
    return None, tally
    
    print "Skipped: %s" % item.getId()
    

def signLease(portal, name):
    """ Creates a folder for the migration. (Deletes any existing one) """

    if hasattr(portal, name):
        portal.manage_delObjects(name)
        
    portal.invokeFactory('Folder', name)
                                
    return portal[name]
    
    
def translate(data):
    """ XXX handle encoding nightmares: this is a terrible hack job. """
    
    #import pdb; pdb.set_trace()
    encodings = ('ascii','utf8','ISO-8859-1')
    exception = True
    
    for encoding in encodings:
        try:
            data = data.decode(encoding)
            exception = False
            break;
        except:
            pass
            
    if exception:
        raise('Encoding error')
        
    return data


def stripDTMLs(id, data):
    """ Strips listed DTML tags out of content """

    for tag in DTMLTAGS:
        hits = data.count(tag)
        if hits > 0:
            print "Replacing %s occurances of %s" % (hits, tag)
            data = data.replace(tag, '')
            
    return data


def removeAllDTML(id, data):
    p = re.compile('<dtml.*?>|</dtml.*?>', re.IGNORECASE)
    matches = p.findall(data)
    if matches:
        
        print "HAS DTML: %s" % id
        print pp(matches)
        print "==================================="
        
    return data


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


                   