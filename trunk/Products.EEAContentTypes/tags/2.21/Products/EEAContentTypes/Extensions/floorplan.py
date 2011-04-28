"""

This files provides a bunch of configuration for the MovingDay script

"""

ROOT = 'Events'
DESTINATION = 'Events-X'

RENDER_DTML = False
STRIP_DTML = True
REMOVE_ALL_DTML = False
TIDY = True

CREATE_DEST = True

# Use this dictionary to map what types of Zope objects
# you want to migrate, and what they should become

# do not include 'folder' if you don't want to recurse

TYPES = {
        'Folder' : 'Folder',         
        'Image' : 'Image',
        'File' : 'File',
        'DTML Document' : 'Document',
        'DTML Method' : 'Document',
        'Call For Tender':'CallForTender',
        'CFT Requestor':'CFTRequestor',
        'Yihaw Event Item' : 'Event'
         }

#this is kinda lazy, but quick-n-dirty
# map your type to the fields' mutator

FIELDMAP = {
            'Image': {'data':'setImage'},
            'File' : {'data' : 'setFile'},
            'DTML Document' : {'method': {'read':'setText'}},
            'DTML Method' : {'method': {'read':'setText'}},
            'Call For Tender' : {'closedate': 'setCloseDate',
                                 'opendate':'setOpenDate',
                                 'nextdoc':'setNextDoc',
                                 'CFI':'setCfi',
                                 'applicationdate':'setApplicationDate',},
            'CFT Requestor' : {'Name':'setName',
                               'Organisation':'setOrganisation',
                               'Address1':'setAddress1',
                               'Address2':'setAddress2',
                               'City':'setCity',
                               'PostCode':'setPostCode',
                               'Country':'setCountry',
                               'Phone':'setPhone',
                               'Fax':'setFax',
                               'Email':'setEmail',
                               'RemoteHost':'setRemoteHost',
                               'RemoteAddr':'setRemoteAddr',},
            'Yihaw Event Item' : { 'Title' : 'setTitle',
                                   'Description' : 'setDescription',
                                   'place' : 'setLocation',
                                   'start_date' : 'setStartDate',
                                   'end_date' : 'setEndDate',
                                   'meeting_URL' : 'setEventUrl'},
            }

DTMLTAGS = ('<dtml-var standard_html_footer>',
            '<dtml-var standard_html_header>',
            '<dtml-var standard_html_header="">',
            '<dtml-var standard_html_footer="">',
            '<dtml-var "pr_footer_info.contact_info">',
            '<dtml-var title_or_id>',
            '<dtml-var title>',
            '<dtml-var document_title>',
            )
