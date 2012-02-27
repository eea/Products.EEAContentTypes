""" Validators """

from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from zope.interface import implements
import PIL
from cStringIO import StringIO
from OFS.Image import Pdata
from Acquisition import aq_base
import re
from Products.Archetypes.interfaces import ISchema

class ManagementPlanCodeValidator:
    """ Validator
    """
    implements(IValidator)

    def __init__(self,
                 name,
                 title='Management plan code',
                 description='Management plan code validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        """ check if management plan code is in right format """
        # check we have 3 digits separated by dots
        errmsg = "Validation failed, management plan code is not in " \
                 "the format #.#.# e.g. 1.5.2"
        digits = value[1].split('.')
        if len(digits) == 3:
            for dig in digits:
                try:
                    int(dig)
                except ValueError:
                    return (errmsg)
            return 1
        else:
            return (errmsg)

validation.register(
    ManagementPlanCodeValidator('management_plan_code_validator'))


class ImageMinSize:
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__( self, name, title='ImageSizeValidator',
                        description='Image size validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check to see if the image is at least 1024px """
        try:
            image = PIL.Image.open(value)
        except AttributeError:
            # OFS Image 
            data = getattr(aq_base(value), 'data')
            if isinstance(data, Pdata):
                data = str(data)
            img_stream = StringIO(data)
            image = PIL.Image.open(img_stream)
        if image.size[0] < 1024:
            return "Image needs to be at least 1024px in width"
        return 1

validation.register(ImageMinSize('imageMinSize'))

def video_cloud_validator(value, instance = None):
    """ check if cloudUrl has a youtube link and construct an iframe out
    of it if it's just a link
    """
    youtube_id = re.compile('[0-9a-zA-z\-_]{6,}[A-Z]{1,}')
    obj_schema = ISchema(instance)
    field = obj_schema['cloudUrl']
    mutator = field.getMutator(instance)
    value = value or ""
    youtube_url = "http://www.youtube.com/watch?v="
    vimeo_url = "http://vimeo.com"

    if 'youtu.be' in value:
        # transform youtu.be links iframe code
        res = youtube_id.findall(value)
        if 'list' in value:
            vid_url = res[0] + '&list=' + res[-1]
        else:
            vid_url = res[0]
        value = youtube_url + vid_url
        #instance.mapping['cloud_url']['youtube'] = vid_url

    elif 'playlist' in value:
        # transform playlist link to iframe code
        res = youtube_id.findall(value)
        playlist = 'http://www.youtube.com/playlist?'
        vid_url = playlist + 'list=' + res[1]
        value = vid_url
        #instance.mapping['cloud_url']['youtube'] = vid_url

    elif ('youtube' in value) and ('iframe' not in value):
        # transform long youtube link to iframe code
        res = youtube_id.findall(value)
        if 'list' in value:
            vid_url = res[0] + '?list=' + res[-1]
        else:
            vid_url = res[0]
        value = youtube_url + vid_url
        #instance.mapping['cloud_url']['youtube'] = vid_url
    elif ('youtube' in value) and ('iframe' in value):
        res = youtube_id.findall(value)
        if 'list' in value:
            vid_url = res[0] + '?list=' + res[-1]
        else:
            vid_url = res[0]
        value = youtube_url + vid_url
        #instance.mapping['cloud_url']['youtube'] = vid_url

    if 'vimeo' in value:
        vimeo = re.compile('[\d]{5,}')
        res = vimeo.findall(value)
        value = vid_url

    mutator(value)

class VideoCloudUrlValidator:
    """ Image minimum size validator
    """
    implements(IValidator)

    def __init__( self, name, title='VideoCloudUrlValidator',
                        description='VideoCloudUrl Validator'):
        self.name = name
        self.title = title or name
        self.description = description

    def __call__(self, value, instance, *args, **kwargs):
        """ check and transform links if we don't get iframe code
        for youtube
        """
        video_cloud_validator(value, instance)

validation.register(VideoCloudUrlValidator('videoCloudUrlValidator'))
