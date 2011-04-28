# -*- coding: utf-8 -*-
#
# File: migrateNews.py
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
from Products.EEAContentTypes.content import Highlight
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

#from Products.EEAContentTypes.content_filter import *

def migrate(self):
    
    visibilityLevel = "middle"
    portal = getToolByName(self,'portal_url').getPortalObject()    
    root = portal['news']
    
    #old ones
    news = getContentTypes(root.objectValues(),'Announcement')
    
    tally = keepTally(root)
    
    #place for new ones
    folder = 'ATNewsHighlights'
    if hasattr(portal, folder):
        portal.manage_delObjects(folder)
        
    portal.invokeFactory('Folder', folder)
    hlf = portal[folder]

    # For debugging.  Shows all highlights and contents
    from pprint import pprint as pp
    pp([(ll.id, [obj.meta_type for obj in ll.objectValues()]) for ll in news])
    
    for ll in news:

        id = ll.id
        print "Migrating %s ... " % id
        
        # gather everything up
        title = ll.title or ll.id
        releasedate = ll.releasedate or None
        teaser = ll.teaser
        details = ll.details
        author = ll.author or None            
    
        expiry = releasedate + 7

        title = safe_unicode(title)
        
        #make it
        try:
            hlf.invokeFactory('Highlight', 
                              id=id, 
                              title=title,
                              description=teaser, 
                              teaser=teaser,
                              visibilityLevel=visibilityLevel,
                              publishDate=releasedate,
                              expirationDate=expiry,
                              author=author,
                              text=details,)
            
            new_hl = hlf[id]
            hlid = new_hl.id
            updateTally(tally, ll, 'migrated')
            
        except:
            pass
        
        files = getContentTypes(ll.objectValues(),'File')
        for x in range(len(files)):
            print "%s has files" % hlid
            
            this_file = files[x]
            fileid = this_file.id()
            
            try:
                new_hl.invokeFactory('File',
                                     id=fileid,
                                     title=this_file.title_or_id())
                
                new_hl[fileid].setFile(this_file)
                updateTally(tally, this_file, 'migrated')                
            except:
                pass

        extra_images = getContentTypes(ll.objectValues(),'Image')
        for x in range(len(extra_images)):
            print "%s has extra images" % hlid
            
            this_image = extra_images[x]
            imageid = this_image.id()
            
            try:
                new_hl.invokeFactory('Image',
                                     id=imageid,
                                     title=this_image.title_or_id())
                
                new_hl[imageid].setImage(this_image)
                updateTally(tally, this_image, 'migrated')
            except:
                pass

        # put all remaining folderfulls INTO our new object
        subfolders = getContentTypes(ll.objectValues(),'Folder')        
        
        for subfolder in subfolders:
            new_hl.invokeFactory('Folder',
                                 id=subfolder.getId(),
                                 title=subfolder.title_or_id())
            tally = updateTally(tally, subfolder, 'migrated')
            subloc = new_hl[subfolder.getId()]
            tally = pack(subfolder.objectValues(), subloc, tally=tally)
        
    
        # push through to published state
        wft =getToolByName(portal, 'portal_workflow')
        wft.doActionFor(new_hl, 'send')
        wft.doActionFor(new_hl, 'publish')
        #print "Migrated! - %s" % newsTitle

    print "Migrating the rest"
    
    #from Products.EEAContentTypes.Extensions.movingDay import pack
    #tally = pack(root.objectValues(), folder, tally=tally)

    print "=============================="
    for k,v in tally.iteritems():
        if v['status'] == 'unmigrated':
            print k
            print v

    print "Done diddly-one!"
    
    