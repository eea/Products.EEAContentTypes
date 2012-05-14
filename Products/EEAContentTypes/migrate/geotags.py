
""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from eea.geotags.interfaces import IGeoTags
import logging
from Products.Archetypes import atapi
#import time
import transaction
logger = logging.getLogger('EEAContentTypes.geotypes.migrate')
from Products.EEAContentTypes.content.interfaces import IGeoPosition 

class LocationMigrate(BrowserView):
    """ Run location migration for events
    """
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog
        folder_path = '/'.join(context.getPhysicalPath())
        depth = 6 if self.context.portal_type == "Folder" else 0
        brains = catalog.searchResults(portal_type = ('QuickEvent', 'Event'),
             path = {'query': folder_path, 'depth': depth}, Language = "all",
                                                        show_inactive = True)
        errors = ["Errors:"]
        not_found = ["Not Found:"]
        no_location = ["No location"]

        count = 0
        for brain in brains:
            try:
                obj = brain.getObject()
                url = obj.absolute_url()
                loc = IGeoPosition(obj)
                geo = IGeoTags(obj)
                location = obj.location
                if type(location) == tuple:
                    location = location[0]
                location = location.encode('utf-8')
                if not location:
                    logger.info("NO Location %s" % url)
                    no_location.append("NO Location %s" % url)
                    continue
                #if len(geo.tags):
                #    continue
                #time.sleep(0.5)

                geo = IGeoTags(obj) 
                name = location
                name_list = name.split(',') 
                template = { 
                    'type': 'FeatureCollection', 
                    'features': [] 
                } 
                feature = { 
                    'type': 'Feature', 
                    'bbox': [], 
                    'geometry': { 
                        'type': 'Point', 
                        'coordinates': [loc.latitude, loc.longitude], 
                        }, 
                    'properties': { 
                        'name': '', 
                        'title': name, 
                        'description': name,
                        'center': [loc.latitude, loc.longitude], 
                        'country': loc.country_code, 
                        'other':{ 
                            'countryCode': loc.country_code, 
                            'countryName': name_list[-1], 
                            'adminName1': name_list[0], 
                            'lat': loc.latitude, 
                            'lng': loc.longitude, 
                            'name': name_list[0], 
                        }, 
                        'tags' : "" 
                        }
                }

                template['features'].append(feature)

                field = obj.getField('location')
                atapi.LinesField.set(field, obj, obj.location)
                geo.tags = template
                obj.reindexObject()

                count += 1
                if count % 10 == 0:
                    logger.info("Committing geotags migration transaction")
                    transaction.commit()
            except Exception, exp:
                message = exp.message
                if not message:
                    message = exp.args
                error_msg = "%s with error: \n %s" % \
                        (url, message)
                logger.info(error_msg)
                errors.append(error_msg)
                continue

        if len(not_found) > 1 or len(no_location) > 1:
            return (not_found, no_location, errors)
        else:
            return errors if len(errors) > 1 else "done"

