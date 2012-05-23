""" Migration script from location widget to geotags
"""
from Products.Five.browser import BrowserView
from eea.geotags.interfaces import IGeoTags
import logging
from Products.Archetypes import atapi
import time
import json
import urllib
import transaction
logger = logging.getLogger('EEAContentTypes.geotypes.migrate')
from Products.EEAContentTypes.content.interfaces import IGeoPositioned
from zope.interface import noLongerProvides
from zope.annotation.interfaces import IAnnotations
from Products.CMFCore.utils import getToolByName

class LocationMigrate(BrowserView):
    """ Run location migration for events
    """
    def __call__(self):
        context = self.context
        catalog = context.portal_catalog
        folder_path = '/'.join(context.getPhysicalPath())
        depth = 6 if self.context.portal_type == "Folder" else 0
        portal_type = self.request.get('type')
        # allow the selection of the portal type from the migration script 
        # EX: http://localhost:8081/www/SITE/@@migrate2geotags?type=Organisation
        if portal_type:
            brains = catalog.searchResults(portal_type = portal_type,
                        path = {'query': folder_path, 'depth': depth},
                            Language ="all", show_inactive = True)
        else:
            brains = catalog.searchResults(portal_type = ('QuickEvent',
                 'Event'), path = {'query': folder_path, 'depth': depth},
                                   Language = "all", show_inactive = True)

        # get the brains from topic result if script is runned on a object
        # that is a topic
        if context.portal_type == 'Topic':
            brains = context.queryCatalog()
        errors = ["ERRORS:"]
        not_found = ["NOT FOUND:"]
        no_location = ["NO LOCATION:"]

        count = 0

        # add yahoo service key so that we can search if yahoo if google 
        # returns no results
        service_keys = {}
        portal_properties = getToolByName(context,
                                          'portal_properties')
        geo_properties = getattr(portal_properties,
                                 'geographical_properties', None)

        service_keys['yahoo_key'] = geo_properties.getProperty(
                'yahoo_key', '')

        for brain in brains:
            try:
                obj = brain.getObject()
                url = obj.absolute_url()
                location = obj.location
                location_len = len(location)
                if type(location) == tuple and location_len:
                    location = location[0]
                if location_len:
                    location = location.encode('utf-8')
                if not location or \
                            location == '<street address>, <city>, <country>':
                    obj.location = ()
                    if IGeoPositioned.providedBy(obj):
                        noLongerProvides(obj, IGeoPositioned)
                    obj.reindexObject()
                    #logger.info("NO Location %s" % url)
                    no_location.append("NO Location %s" % url)
                    continue

                template = {
                    'type': 'FeatureCollection',
                    'features': []
                }
                # check if geoposition information is already set on the object
                # and if so we make a geotag from the current information
                anno = IAnnotations(obj)
                anno_loc = anno.get(['coordonates'])
                anno_country = anno.get(['country_code'])
                name = location
                name_list = name.split(',')
                if anno_loc and anno_country:
                    latitude = anno_loc.get('latitude')
                    longitude = anno_loc.get('longitude')
                    country_code = anno_country.get('country_code')
                    feature = self.find_location(latitude, longitude,
                                            country_code, name, name_list)
                    # remove these entries from annotation as they
                    # are no longer needed, and remove IGeoPositioned  
                    del(anno[['coordonates']])
                    del(anno[['country_code']])
                    noLongerProvides(obj, IGeoPositioned)
                else:
                    # search with google geoposition information for
                    # current location
                    time.sleep(1.0)
                    params = {
                              'address': location,
                              'sensor' : 'false'}
                    u = urllib.urlopen(
                      "http://maps.googleapis.com/maps/api/geocode/json?%s" % \
                                                      urllib.urlencode(params))
                    gbuffer = u.read()
                    js = json.loads(gbuffer)
                    res = js.get('results')
                    if res:
                        res = res[0]
                        loc = res['geometry']['location']
                        viewport = res['geometry']['viewport']
                        ne = viewport['northeast']
                        sw = viewport['southwest']
                        bbox = [sw['lat'], sw['lng'], ne['lat'], ne['lng']]
                        title = res['address_components'][0]['long_name']
                        feature = {
                            'type': 'Feature',
                            'bbox': bbox,
                            'geometry': {
                                'type': 'Point',
                                'coordinates': [loc['lat'], loc['lng']],
                                },
                            'properties': {
                                'name': location,
                                'title': title,
                                'description': location,
                                'center': [loc['lat'], loc['lng']],
                                'other': res,
                                'tags' : res['types']
                            }
                        }
                    else:
                        # if google returns no result then we use 
                        # yahoo geocode search
                        params = {
                                  'q': location,
                                  'appid' : service_keys['yahoo_key'],
                                  'flags' : 'J'}
                        u = urllib.urlopen(
                          "http://where.yahooapis.com/geocode?%s" % \
                                                    urllib.urlencode(params))
                        ybuffer = u.read()
                        js = json.loads(ybuffer)
                        res = js['ResultSet'].get('Results')
                        if res:
                            res = res[0]
                            latitude = res.get('latitude')
                            longitude = res.get('longitude')
                            country_code = res.get('countrycode')
                            feature = self.find_location(latitude, longitude,
                                                  country_code, name, name_list)
                        # no geocode was found for the given location
                        else:
                            item = "url: %s  location: %s" % (url, obj.location)
                            logger.info("NOT FOUND: %s" % item)
                            not_found.append(item)
                            # add the curent location to the lines field so that
                            # we don't repeat over the string location
                            field = obj.getField('location')
                            atapi.LinesField.set(field, obj, obj.location)
                            if IGeoPositioned.providedBy(obj):
                                noLongerProvides(obj, IGeoPositioned)
                            obj.reindexObject()
                            continue

                geo = IGeoTags(obj)

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

        logger.info("Migration to geotags DONE")
        if len(not_found) > 1 or len(no_location) > 1:
            return (not_found, no_location, errors)
        else:
            return errors if len(errors) > 1 else "done"

    def find_location(self, latitude, longitude, country_code, name,
                                                            name_list):
        """ Returns a feature dict for the given input
        """
        feature = {
            'type': 'Feature',
            'bbox': [],
            'geometry': {
                'type': 'Point',
                'coordinates': [latitude, longitude],
                },
            'properties': {
                'name': '',
                'title': name,
                'description': name,
                'center': [latitude, longitude],
                'country': country_code,
                'other':{
                    'countryCode': country_code,
                    'countryName': name_list[-1],
                    'adminName1': name_list[0],
                    'lat': latitude,
                    'lng': longitude,
                    'name': name_list[0],
                },
                'tags' : ""
            }
        }
        return feature
