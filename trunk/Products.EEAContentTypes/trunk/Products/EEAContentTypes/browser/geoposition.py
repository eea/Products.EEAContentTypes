""" Geo position
"""
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.EEAContentTypes.content.interfaces import IGeoPosition
from Products.EEAContentTypes.content.interfaces import IGeoPositioned
from Products.Five.browser import BrowserView
from Products.EEAContentTypes.browser.interfaces import (
    IGeoMapData,
    IGeoMapView,
    IGeoConverter
)
from Products.EEAContentTypes.browser.interfaces import (
    IGeoPositionView,
    IGoogleEarthView
)
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtility
from zope.interface import implements
import logging
from plone.i18n.locales.interfaces import ICountryAvailability

from eea.themecentre.interfaces import IThemeTagging
from eea.geotags.interfaces import IGeoTags, IGeoTagged

logger = logging.getLogger('Products.EEAContentTypes.browser.geoposition')



class GeoLocationTools(BrowserView):
    """ Geo location tools
    """
    def isGeoContainer(self):
        """ Is geo container?
        """
        syn = getToolByName(self.context, 'portal_syndication')
        context = self.context
        if hasattr(context, 'context'):
            context = context.context
        catalog = getToolByName(context, 'portal_catalog')

        if not syn.isSyndicationAllowed(context):
            return False

        if context.meta_type == 'ATTopic':
            res = context.queryCatalog()
            # check if result of topic query contains events
            if res:
                res = 'true' if \
                    'Products.ATContentTypes.interfaces.event.IATEvent' \
                 in res[0].object_provides else ''
        else:
            path = '/'.join(self.context.getPhysicalPath())
            res = catalog.searchResults({
                        'path': {'query': path, 'depth': 1},
                        'object_provides':
                        'Products.ATContentTypes.interfaces.event.IATEvent'
                        })
        if len(res):
            return True
        return False


class GoogleEarthView(object):
    """ Google Earth View """

    implements(IGoogleEarthView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        res = []
        placemarkers = []
        detect_flag = False
        res_add = res.append
        placemarkers_add = placemarkers.append

        if IGeoTagged.providedBy(self.context):
            detect_flag = True

        if detect_flag:
            placemarkers_add(self.context)
        else:
            syn = getToolByName(self.context, 'portal_syndication')
            default_max = syn.getMaxItems()
            maxi = syn.getMaxItems(self.context)
            maxi = type(maxi) == type(1) and maxi or default_max
            objects = list(syn.getSyndicatableContent(self.context))[:maxi]

            for obj in objects:
                if "eea.geotags.storage.interfaces.IGeoTagged" \
                                                    in obj.object_provides:
                    placemarkers_add(obj)

        for places in placemarkers:
            obj = places.getObject()
            placemark_url = obj.event_url()
            geotags = IGeoTags(obj).tags
            geotags = geotags['features'][0].get('geometry', {}) \
                                                          .get('coordinates')
            geotags = geotags if geotags else [0, 0]
            location = obj.location
            location = "# ".join(location) if type(location) == tuple else \
                                                                      location
            if not placemark_url.startswith('http://'):
                placemark_url = 'http://%s' % placemark_url

            kml_info = {'placemark_title':       obj.Title(),
                        'placemark_description': obj.Description(),
                        'placemark_location':    location,
                        'placemark_url':         placemark_url,
                        'placemark_latitude':    geotags[0],
                        'placemark_longitude':   geotags[1]}

            res_add(kml_info)

        return res


class GeoPositionView(BrowserView):
    """ Geo Position View """

    implements(IGeoPositionView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        map_template = ''
        api_key = ''
        geoobject = IGeoPosition(self.context)
        obj_url = self.context.event_url()
        #if not obj_url.startswith('http://'):
            # TODO: check this assigment
            #placemarkobj_url = 'http://%s' % obj_url

        portal_properties = getToolByName(self, 'portal_properties')
        geo_properties = getattr(portal_properties, 'geographical_properties')
        map_to_use = geo_properties.getProperty('map_service_to_use', '')

        if map_to_use != 'None':
            if map_to_use.find('Yahoo') > -1:
                map_template = YAHOO_SINGLE_TPL
                api_key = geo_properties.getProperty('yahoo_key', '')
            elif map_to_use.find('Google') > -1:
                map_template = GOOGLE_SINGLE_TPL
                api_key = geo_properties.getProperty('google_key', '')

        # TODO: if no external URL the 'Read more'
        # link to be hiddden on maps info
        location = self.context.location
        if isinstance(location, (tuple, list)):
            location = ', '.join(location)

        map_data = {'api_key':      api_key,
                    'latitude':     geoobject.latitude,
                    'longitude':    geoobject.longitude,
                    'location':     location.encode('utf-8'),
                    'external_url': obj_url,
                    'point_zoom':   geo_properties.getProperty(
                        'PointZoom_single', 'null') or 'null',
                    'map_loc':      geo_properties.getProperty(
                        'MapLoc_single', 'null') or 'null',
                    'map_zoom':     geo_properties.getProperty(
                        'MapZoom_single', 'null') or 'null'}

        res = map_template % map_data
        return res


class GeoConverter(BrowserView):
    """ Geo converter """
    implements(IGeoConverter)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def geoConvert(self, data):
        """ Geo convert
        """
        res = ''
        for item in data:
            try:
                obj = item.getObject()
            except Exception:
                obj = item
            if IGeoPositioned.providedBy(obj):
                geoobject = IGeoPosition(obj)
                res += "%s|%s###" % (geoobject.latitude, geoobject.longitude)

        return '<script type="text/javascript">var geo_data = "%s"</script>' % (
            res,)


class GeoMapData(BrowserView):
    """ Geo map data """
    implements(IGeoMapData)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, cc=None, tc=None, **kwargs):
        #TODO: kwargs to be used for filter call
        props = getToolByName(self.context, 'portal_properties').site_properties
        placemarkers = []
        placemarkers_add = placemarkers.append
        res = []
        res_add = res.append
        tmp_identical = {}
        res_html = []
        reshtml_add = res_html.append

        syn = getToolByName(self.context, 'portal_syndication')
        default_max = syn.getMaxItems()
        maxi = syn.getMaxItems(self.context)
        maxi = type(maxi) == type(1) and maxi or default_max
        objects = list(syn.getSyndicatableContent(self.context))[:maxi]
        ### plone4.1 couldn't find the interface brovided by brains
        ### so we are asking for the objects
        objects = [obj.getObject() for obj in objects]

        for obj in objects:
            geotags = IGeoTags(obj).tags
            if geotags.get('features'):
                placemarkers_add(obj)

        # Country widget
        country_inf = {}
        country_html = ''

        #plone4, migrated with the following code, needs checks
        #country_list = getCountries()
        country_util = getUtility(ICountryAvailability, context=self.context)
        country_list = dict(country_util.getCountryListing())

        country_inf_sort = {}
        country_filter = cc

        # Theme widget
        theme_html = ''
        theme_inf_sort = {}
        theme_filter = tc

        # Create map markers
        vocabFactory = getUtility(IVocabularyFactory, name="Allowed themes")
        themeVocab = vocabFactory(self)
        for obj in placemarkers:
            # #3355 get first geotag for the events map
            geotags = IGeoTags(obj).tags
            geoobject = geotags['features'][0]['properties']
            country_code = geoobject.get('country', '')
            try:
                country_code = country_code if country_code else \
                    geoobject['other']['address_components'][-1]['short_name']
            except Exception:
                # no country code exists so we skip this item
                continue
            country_name = country_list.get(country_code.lower(), '')

            if country_code:
                country_inf[country_code] = country_inf.get(country_code, 0)
                country_inf[country_code] += 1
                # Set country widget info
                country_inf_sort[country_name] = country_code
            else:
                country_inf['Other'] = country_inf.get('Other', 0)
                country_inf['Other'] += 1

            # Set theme widget info
            obj_theme = []
            obj_theme.extend(IThemeTagging(obj).tags)
            for th in obj_theme:
                if th != 'default':
                    th_count = theme_inf_sort.get(th, 0)
                    if th_count == 0:
                        th_count = 1
                    else:
                        th_count = th_count[1] + 1
                    theme_inf_sort[th] = (themeVocab.getTerm(th).title,
                                          th_count)

            if ((country_filter is not None and country_filter == country_code)
                or (country_filter is None)) and \
               ((theme_filter is None) or (theme_filter is not None
                                           and theme_filter in obj_theme)):

                ob_lat = geoobject.get('lat')
                ob_lat = ob_lat if ob_lat else geoobject['center'][0]
                ob_long = geoobject.get('lng')
                ob_long = ob_long if ob_long else geoobject['center'][1]

                if (ob_lat, ob_long) in tmp_identical.keys():
                    if float(ob_long) > 0:
                        ob_long = str(float(ob_long) + 0.02)
                    else:
                        ob_long = str(float(ob_long) - 0.02)
                    while (ob_lat, ob_long) in tmp_identical.keys():
                        if float(ob_long) > 0:
                            ob_long = str(float(ob_long) + 0.02)
                        else:
                            ob_long = str(float(ob_long) - 0.02)

                tmp_identical[(ob_lat, ob_long)] = obj.id
                res_add('%s|%s|mk_%s|%s|%s' % (ob_lat,
                                               ob_long,
                                               obj.id,
                                               obj.Title().decode('utf-8'),
                                               'mk_GEOTYPE'))

                obj_desc = obj.Description()
                if len(obj_desc) > 550:
                    obj_desc = obj_desc[:550] + ' ...'
                start_date = DateTime(obj.start()).strftime(
                    props.localLongTimeFormat)
                end_date = DateTime(obj.end()).strftime(
                    props.localLongTimeFormat)

                location = obj.location
                if isinstance(location, (tuple, list)):
                    location = u', '.join(location)
                reshtml_add(YAHOO_MULTI_MARKER_TPL % {
                    'id': 'mk_%s' % obj.id,
                    'title': obj.Title(),
                    'description': obj_desc,
                    'location': location.encode('utf-8'),
                    'period': '%s to %s' % (start_date, end_date),
                    'link': obj.absolute_url()})

        # Generate country widget content
        cc_list = country_inf_sort.keys()
        cc_list.sort()
        for country_name in cc_list:
            country_code = country_inf_sort.get(country_name, '')
            country_html += ('<span class="widget_row" id="%s" '
                'onclick="javascript:selectCountry(this);">%s (%s)</span>') % (
                country_code, country_name, country_inf[country_code])
        if country_inf.get('Other', None):
            country_html += '<br/><span>%s (%s)</span>' % (
                'Other', country_inf['Other'])

        # Themes filtering
        th_list = theme_inf_sort.keys()
        th_list.sort()

        for th in th_list:
            th_info = theme_inf_sort[th]
            theme_html += ('<span class="widget_row" id="%s" '
                'onclick="javascript:selectTheme(this);">%s (%s)</span>') % (
                    th, th_info[0], th_info[1])

        result = '%s' % '###'.join(res)
        result += '####%s' % ''.join(res_html).decode('utf8')
        result += '####%s' % country_html
        result += '####%s' % theme_html
        return result


class GeoMapView(BrowserView):
    """ Geo map view """

    implements(IGeoMapView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        map_template = ''
        api_key = ''
        if hasattr(self.context, 'context'):
            self.context = self.context.context
        pu = getToolByName(self.context, 'portal_url')
        #portal = pu.getPortalObject()
        portal_url = pu.absolute_url()

        portal_properties = getToolByName(self, 'portal_properties')
        geo_properties = getattr(portal_properties, 'geographical_properties')
        map_to_use = geo_properties.getProperty('map_service_to_use', '')

        if map_to_use != 'None':
            if map_to_use.find('Yahoo') > -1:
                map_template = YAHOO_MULTI_TPL
                api_key = geo_properties.getProperty('yahoo_key', '')
            #TODO: add/create Google template
            elif map_to_use.find('Google') > -1:
                map_template = YAHOO_MULTI_TPL
                api_key = geo_properties.getProperty('yahoo_key', '')
                #api_key = geo_properties.getProperty('google_key', '')

        map_data = {'api_key':      api_key,
                    'map_loc':      geo_properties.getProperty(
                        'MapLoc_multi', ''),
                    'map_zoom':     geo_properties.getProperty(
                        'MapZoom_multi', ''),
                    'context_url':  self.context.absolute_url(),
                    'portal_url':   portal_url}

        return map_template % map_data

YAHOO_MULTI_MARKER_TPL = """
<div id="%(id)s" class="marker">
                       <div class="marker-body">
                       <h3>%(title)s</h3>
                       <div class="marker-loc">
                       <small><strong>Location: </strong>%(location)s</small>
                       </div>
                       <div class="marker-loc">
                       <small><strong>Period: </strong>%(period)s</small>
                       </div>
                       <small>%(description)s</small>
                       <div class="marker-more">
                       <a href="%(link)s">read more</a>
                       </div>
                       </div>
</div>
"""

YAHOO_MULTI_TPL = """
<style type="text/css">
.widget_title {
                text-align: center;
                font-weight: bold;
                border-bottom: 1px solid black;
                padding-bottom: 3px;
                margin-bottom: 3px;
}

.widget_row {
                cursor: pointer;
                display: block;
}

.widget_row:hover {
                background-color: orange;
}

.widget_tip {
                position: absolute;
                bottom: 5px;
                right: 5px;
                -moz-opacity: 1;
                color: black;
                font-size: 0.8em;
                filter: alpha (opacity=100)
                cursor: pointer;
                background-color: #ccc;
                padding: 1px 3px 1px 3px;
}

.widget_tip:hover {
                background-color: orange;
}

#map_left_widget {
                position: absolute;
                top: 90px;
                left: 10px;
                z-index: 99;
                border: 1px solid black;
                background-color: #f0f0f0;
                height: 160px;
                -moz-opacity: 0.6;
                padding: 5px 4px 2px 4px;
                filter: alpha (opacity=60);
                overflow: hidden;
}

#map_right_widget {
                position: absolute;
                top: 30px;
                right: 10px;
                z-index: 99;
                border: 1px solid black;
                background-color: #f0f0f0;
                height: 235px;
                -moz-opacity: 0.6;
                padding: 4px 4px 2px 4px;
                filter: alpha (opacity=60);
}

* html #map_right_widget #country_info {
                width: 150px;
}
* html #map_left_widget #theme_info {
                width: 210px;
}

*:first-child+html #map_right_widget #country_info {
                width: 150px;
}
*:first-child+html #map_left_widget #theme_info {
                width: 210px;
}

#map_right_widget #country_info {
                overflow: auto;
                height: 195px;
}
#map_left_widget #theme_info {
                overflow: auto;
                height: 132px;
}

#map_events_yahoo hr {
                color: black;
                background-color: black;
                height: 2px;
                padding: 0;
                margin: 4px;
                /* margin: 0; for IE7 */
                width: 70px; /* for IE7*/
}
#map_events_yahoo table {
    display: table;
}
div.marker {
                display: none;
}
div.marker-body {
                width: 290px;
                margin-top: 0;
}
div.marker-more {
                padding: 10px 5px 5px 15px;
}
div.marker-loc {
                padding-bottom: 5px;
}
div.marker-body h3 {
                font-weight: bold;
                font-size: 1em;
                margin-top: 0;
                padding-top: 0;
                text-transform: uppercase;
}
#map_center_widget {
                display: inline;
                cursor: pointer;
                background-color: black;
                border: 1px solid black;
                height: 15px;
                opacity:0.5;
                padding: 0 2px;
                position: relative;
                left: 70px;
                top: -295px;
                z-index: 99;
                color: #DDD;
                line-height: 1.2em;
                filter: alpha (opacity=50);
                font-weight: bold;
}

.map_left_widget_header {
                border: 0px none ;
                display: inline;
                cursor: pointer;
                padding-top: 5px;
                height: 1em;
                font-weight: bold;
                background-color: transparent;
}

#themes-close, #country-close {
    background: none repeat scroll 0 0 #CCCCCC;
    height: 20px;
    left: 16px;
    padding: 3px;
    position: relative;
    top: 235px;
    width: 30px;
    z-index: 5000;
}
#country-close {
    top: 249px;
    left: 455px;
    height: 18px;
}
a#themes-close:hover, a#country-close:hover {
    background: orange !important;
    color: #000;
}
a#themes-close:visited, a#country-close:visited {
    color: #000;
}
</style>

<div style="display:none" id="map_markers"></div>
<script type="text/javascript"
    src="http://api.maps.yahoo.com/ajaxymap?v=3.7&appid=%(api_key)s"></script>

<div id="map_events_yahoo" style="border: 1px solid black">
    <span id="map_left_widget" style="display:none">
    <span class="map_left_widget_header">Filter by theme</span>
    <div id="theme_info"></div>
    <div class="widget_tip"
        onclick="javascript:deselectAll('theme');">Show all</div>
    </span>
    <a href="#" id="themes-close">Close</a>
    <span id="map_right_widget" style="display:none">
    <div id="country_info"></div>
    <div class="widget_tip"
        onclick="javascript:deselectAll('country');">Show all</div>
    </span>
    <a href="#" id="country-close">Close</a>
</div>

<center style="margin-right: 10em">
<span id="map_center_widget" style="">
  <span id="record_counter">0</span> events on map</span>
</center>

<script type="text/javascript">
    <!--
    var thc = jQuery("#themes-close, #country-close"),
        maps = jQuery("#map_left_widget, #map_right_widget");
    thc.toggle(function(e) {
        e.preventDefault();
        maps.fadeOut('slow');
        thc.text("Show");
    }, function(e){
        e.preventDefault();
        maps.fadeIn('slow');
        thc.text("Close");
    });

    var xmlhttp;
    var map = null;
    var country_filter = '';
    var theme_filter = '';

    function handlerYahooMap() {
    var mapCenterLoc = "%(map_loc)s", mapCenterZoom = %(map_zoom)s+11;
    map = new YMap(document.getElementById("map_events_yahoo"), YAHOO_MAP_REG);
    // Set map container height and width
    document.getElementById("map_events_yahoo").style.width = '99%%';
    document.getElementById("map_events_yahoo").style.height = '300px';
    // Display the map centered on given address
    map.drawZoomAndCenter(mapCenterLoc, mapCenterZoom);
    map.addTypeControl();
    map.addPanControl();
    map.addZoomLong();
    map.disableKeyControls();

    //markers
    //#TODO: define markers type

    var zp = new YCoordPoint(100,100);
    zp.translate('left','bottom');
    var cOverlay = new YCustomOverlay(zp);
    showSelectedLocations();

    document.getElementById("map_left_widget").style.display = 'inline';
    document.getElementById("map_right_widget").style.display = 'inline';
    }

    function initXMLdoc() {
    xmlhttp = null;
    if (window.XMLHttpRequest) {
    xmlhttp=new XMLHttpRequest()
    }
    else if (window.ActiveXObject) {
    xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    }

    function loadXMLDoc(url, handler) {
    initXMLdoc();
    function wrapper()
    {
    if (xmlhttp.readyState == 4) {
    if (xmlhttp.status == 200) {
    handler();
    return true;
    } else {
    alert('GeoMap, there was a problem retrieving the XML data:' +
           xmlhttp.statusText);
    return false;
    }
    }
    }
    if (xmlhttp != null)
    {
    xmlhttp.onreadystatechange = wrapper;
    xmlhttp.open("GET", url, true);
    xmlhttp.send(null);
    }
    }

    function trim(str) {
    var ret;
    if(typeof(str) != "string") str = str + "";
    return str.replace(/(^\s+)|(\s+$)/gi, "");
    }

    function createMarker(map, lat, lng, id) {
    var geo_loc = new YGeoPoint(lat, lng);
    var geo_image = new YImage();
    geo_image.src = '%(portal_url)s/event_icon.gif';
    geo_image.size = new YSize(16,16);

    var marker = new YMarker(geo_loc, geo_image)
    marker.setSmartWindowColor("grey");
    YEvent.Capture(marker, EventsList.MouseClick, function() {
    marker.openSmartWindow(document.getElementById(id).innerHTML);});
    map.addOverlay(marker);

    return marker.id
    }

    function showSelectedLocations_request_handler(filter)
    {
    var mapMarker = null;
    // clear map
    map.removeMarkersAll();

    // set markers
    var data = xmlhttp.responseText.split('####'), b = '', c = '', d = '';
    b = trim(data[1]);
    if (b != '') document.getElementById('map_markers').innerHTML = b;

    // set country widget
    if (country_filter == '') {
    c = trim(data[2]);
    if (c != '') document.getElementById('country_info').innerHTML = c;
    }

    // set theme widget
    if (theme_filter == '') {
    d = trim(data[3]);
    if (d != '') document.getElementById('theme_info').innerHTML = d;
    }

    // put markers on map
    var arrMarkers = trim(data[0]).split('###');
    var num_records = 0;
    for (var i = 0; i < arrMarkers.length; i++) {
    var b = trim(arrMarkers[i]);
    if (b != '') {
    var m = b.split('|');
    lat = parseFloat(m[0]);
    lng = parseFloat(m[1]);
    id = m[2].toString();
    label = m[3].toString();
    mapMarker = m[4].toString();
    mapid = createMarker(map, lat, lng, id);
    num_records++;
    }
    }

    // update record counter
    // if (country_filter == '') document.getElementById('record_counter')
    //   .innerHTML = num_records.toString();
    document.getElementById('record_counter')
        .innerHTML = num_records.toString();
    }

    function showSelectedLocations() {
    loadXMLDoc('%(context_url)s/geoEventsData' + createQuery(),
        showSelectedLocations_request_handler);
    }

    function testSelected(elem_color) {
    return elem_color == "#c8e368" || elem_color == "rgb(200, 227, 104)";
    }

    function selectCountry(elem) {
    if (testSelected(elem.style.backgroundColor)) {
    elem.style.backgroundColor = "";
    country_filter = '';
    }
    else {
    country_list = document.getElementById("country_info")
      .getElementsByTagName("span");
    for (var i = 0; i < country_list.length; i++) {
    country_list[i].style.backgroundColor = "";
    }
    elem.style.backgroundColor = "#C8E368";
    country_filter = elem.id;
    }
    showSelectedLocations()
    }

    function selectTheme(elem) {
    if (testSelected(elem.style.backgroundColor)) {
    elem.style.backgroundColor = "";
    theme_filter = '';
    }
    else {
    theme_list = document.getElementById("theme_info")
        .getElementsByTagName("span");
    for (var i = 0; i < theme_list.length; i++) {
    theme_list[i].style.backgroundColor = "";
    }
    elem.style.backgroundColor = "#C8E368";
    theme_filter = elem.id;
    }
    showSelectedLocations()
    }

    function deselectAll(widget) {
    var widget_id = widget + '_info';
    var elem_list = document.getElementById(widget_id)
        .getElementsByTagName("span");
    for (var i = 0; i < elem_list.length; i++) {
    elem_list[i].style.backgroundColor = "";
    }
    showSelectedLocations()
    }

    function createQuery() {
    var query = "";

    // Create themes query
    var theme_list = document.getElementById("theme_info")
        .getElementsByTagName("span");
    for (var i = 0; i < theme_list.length; i++) {
    if (testSelected(theme_list[i].style.backgroundColor)) {
    query = "tc=" + theme_list[i].id;
    break;
    }
    }

    // Create country query
    var country_list = document.getElementById("country_info")
        .getElementsByTagName("span");
    for (var i = 0; i < country_list.length; i++) {
    if (testSelected(country_list[i].style.backgroundColor)) {
    query += "&cc=" + country_list[i].id;
    break;
    }
    }

    if (query != "") query = "?" + query;
    return query;
    }

    var geo_onload=window.onload;
    if (typeof(geo_onload)=='function')
    window.onload=function(){geo_onload();handlerYahooMap()};
    else window.onload=function(){handlerYahooMap()};
    // -->
</script>
"""

YAHOO_SINGLE_TPL = """
<script type="text/javascript"
    src="http://api.maps.yahoo.com/ajaxymap?v=3.7&appid=%(api_key)s"></script>
<div class="mapContainer">
    <div id="map_yahoo"></div>
    <br />
    <a href="http://developer.yahoo.com/about"
        title="Yahoo.com | About Applications that Use Yahoo! Web Services">
        Service provided by Yahoo!
    </a>
</div>
<script type="text/javascript">
    <!--
    function handlerYahooMapSingle() {
    var map = null;
    var PointLat = "%(latitude)s", PointLon = "%(longitude)s";
    var PointZoom = %(point_zoom)s, MapLoc = "%(map_loc)s";
    var MapZoom = %(map_zoom)s+10;
    map = new YMap(document.getElementById("map_yahoo"));
    map.addTypeControl();
    map.addZoomLong();
    map.addPanControl();
    map.setMapType(YAHOO_MAP_REG);

    if (PointLat == 0.0 || PointLon == 0.0) {
    map.drawZoomAndCenter(MapLoc, MapZoom); }
    else {
        marker = new YGeoPoint(PointLat, PointLon);
        map.drawZoomAndCenter(marker, PointZoom);
        map.addMarker(map.getCenterLatLon());
        map.showSmartWindow(marker, '<span>%(location)s</span>' +
         '<br /><p><a href="%(external_url)s" title="">Read more info</a></p>');
       }
    }

    var geo_onload=window.onload;
    if (typeof(geo_onload)=='function')
    window.onload=function(){geo_onload();handlerYahooMapSingle()};
    else window.onload=function(){handlerYahooMapSingle()};
    // -->
</script>
"""

GOOGLE_SINGLE_TPL = """
<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=%(api_key)s"
    type="text/javascript"></script>
<div class="mapContainer">
    <div id="map_google"></div>
    <br />
    <a href="http://code.google.com/apis/maps/terms.html"
      title="Google Maps API Terms of Service - Google Maps API - Google Code">
      Service provided by Google!
    </a>
</div>
<script type="text/javascript">
    <!--
    function handlerGoogleMap() {
    var location = "%(location)s";
    var location_url = "%(external_url)s";
    var latitude = %(latitude)s;
    var longitude = %(longitude)s;
    var map_zoom = %(map_zoom)s;
    var marker_text = location;
    marker_text += '<br/><a href="' + location_url + '">Read more info</a>'

    function html_data(){
    var data = document.createElement("span");
    data.innerHTML = marker_text;
    return data;
    }

    if (GBrowserIsCompatible()) {
    //Set map
    var map = new GMap2(document.getElementById("map_google"));
    map.setCenter(new GLatLng(latitude, longitude), map_zoom);
    map.enableScrollWheelZoom();
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());

    //Draw bubble info
    map.openInfoWindow(map.getCenter(), html_data());

    //Add marker
    function createMarker(latlng) {
    var marker = new GMarker(latlng);
    GEvent.addListener(marker,"click", function() {
    var myHtml = marker_text;
    map.openInfoWindowHtml(latlng, myHtml);
    });
    return marker;
    }
    var point = new GLatLng(latitude, longitude);
    map.addOverlay(createMarker(point));
    }
    else { alert('Incompatible browser'); }
    }

    var geo_onload=window.onload;
    if (typeof(geo_onload)=='function')
    window.onload=function(){geo_onload();handlerGoogleMap()};
    else window.onload=function(){handlerGoogleMap()};

    var geo_unload=window.onunload;
    if (typeof(geo_unload)=='function')
    window.onunload=function(){GUnload();geo_unload();};
    else window.onunload=function(){GUnload()};
    // -->
</script>
"""
