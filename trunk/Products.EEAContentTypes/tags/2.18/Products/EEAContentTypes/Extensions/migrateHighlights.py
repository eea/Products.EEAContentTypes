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

from Products.EEAContentTypes.Extensions.migrationUtils import *
from Products.EEAContentTypes.Extensions.movingDay import pack
from Products.EEAContentTypes.content import Highlight
from Products.CMFCore.utils import getToolByName


from DateTime import DateTime

def migrate(self):
    
    visibilityLevel = "middle"
    portal = getToolByName(self,'portal_url').getPortalObject()    
    root = portal['Highlights']
    
    #old ones
    lowlights = root.objectValues()
    
    tally = keepTally(root)
    
    #place for new ones
    folder = createHolder(portal, 'ATHighlights')

    # For debugging.  Shows all highlights and contents
    from pprint import pprint as pp
    pp([(ll.id, [obj.meta_type for obj in ll.objectValues()]) for ll in lowlights])
    
    for ll in lowlights:

        body = ''    
        dtmls = getContentTypes(ll.objectValues(),'DTML Document')

        print "Starting %s..." % ll.id

        # if there's a DTML document in the highlight
        # put that in as the body.
        if dtmls:
            
            print "##############################################################"
            print "# Object %s has dtml subobjects" % (ll.id)  

            for obj in dtmls:
                
                print obj.id()

                body += stripDTML(obj.document_src())
                body = htmldecode(body)
                body = migrateURL(body)
                body = miniTidy(body)
                
                tally = updateTally(tally, obj, 'migrated')
        
        # massage therapist        
        description = ll.description 
        description = reencode(ll, description, 'description')
        
        title = ll.title
        title = htmldecode(title)

        title = reencode(ll, title, 'title')

        teaser = ll.HTML_here or ll.description
        teaser = reencode(ll, teaser, 'teaser')
        
        values = {}

        print "Migrating %s ... " % ll.id 
        values['id'] = reencode(ll, ll.id, 'id')
        values['description'] = ll.description 
        values['title'] = title
        values['teaser'] = teaser
        values['text'] = body
        values['visibilityLevel'] = visibilityLevel
        values['publishDate'] = ll.publishdate
        values['expiry'] = ll.publishdate + 7
        values['author'] = ''
        values['themes'] = 'Default'
        values['url'] = ll.link
        
        published = ll.published

        # grrrr
        try:
            values['title'].decode('ascii')
        except:
            print "FORCING SAFE ENCODE :("            
            values['title'] = safe_unicode(values['title'])

        # make it
        new_hl = makeMigratedObject(folder, 'Highlight', values)
        
        tally = updateTally(tally, ll, 'migrated')
        
        # deal with the images
        image = None        
        images = getContentTypes(ll.objectValues(),'Image')

        if images:
            image = images[0]
            extra_images = images[1:]
    
        # add the image if we have one
        if image:
            print "Setting %s into %s's image field" % (image.title_or_id(), hlid)
            new_hl.setImage(image)
            tally = updateTally(tally, image, 'migrated')

        if images and extra_images:
            for x in range(len(extra_images)):
                print "%s has extra images" % hlid
                
                this_image = extra_images[x]
                imageid = this_image.id()
                
                new_hl.invokeFactory('Image',
                                     id=imageid,
                                     title=this_image.title_or_id())
                
                new_hl[imageid].setImage(this_image)
                
                tally = updateTally(tally, this_image, 'migrated')

        # put all remaining files INTO our new object
        files = getContentTypes(ll.objectValues(),'File')        
        hlid = new_hl.id
        
        for x in range(len(files)):

            this_file = files[x]
            fileid = this_file.id()
            
            print "%s has files: %s" % (hlid, fileid)
            
            new_hl.invokeFactory('File',
                                 id=fileid,
                                 title=this_file.title_or_id())
            
            new_hl[fileid].setFile(this_file)

            tally = updateTally(tally, this_file, 'migrated')

        # put all remaining folderfulls INTO our new object
        subfolders = getContentTypes(ll.objectValues(),'Folder')        
        
        for subfolder in subfolders:
            new_hl.invokeFactory('Folder',
                                 id=subfolder.getId(),
                                 title=subfolder.title_or_id())
            tally = updateTally(tally, subfolder, 'migrated')
            subloc = new_hl[subfolder.getId()]
            tally = pack(subfolder.objectValues(), subloc, tally=tally)
        
        if published:
            publishContent(portal, new_hl)

        print "Migrated %s\n%s" % (hlid, values['title'])
        print 
        print "================================="
        print

    print "TALLY:\n%s\n" % tally
    
    for k,v in tally.iteritems():
        if v['status'] == 'unmigrated':
            print k
            print tally[k]
        
    print "Done diddly done!"
