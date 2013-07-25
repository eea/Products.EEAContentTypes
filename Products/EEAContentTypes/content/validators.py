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

from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
KEY = 'eea.mediacentre.multimedia'

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
    """ check if cloudUrl has a youtube or vimeo link, saves the id
    in an annotation and save a clean link to the video for the field
    """
    obj_schema = ISchema(instance)
    field = obj_schema['cloudUrl']
    mutator = field.getMutator(instance)
    if value:
        youtube_id = re.compile(r'[0-9a-zA-z\-_]{8,}[A-Z]*')
        youtube_url = "http://www.youtube.com/watch?v="
        vimeo_url = "http://vimeo.com/"

        annotations = IAnnotations(instance)
        mapping = annotations.get(KEY)
        if mapping is None:
            cloud_url =  { 'cloud_url': PersistentDict() }
            mapping = annotations[KEY] = PersistentDict(cloud_url)

        if ('youtu' and 'playlist' in value):
            # transform youtube playlist link 
            res = youtube_id.findall(value)[1]
            vid_id = 'videoseries&' + 'list=' + res
            value = 'http://www.youtube.com/playlist?list=' + res
            mapping['cloud_url']['youtube'] = vid_id

        elif ('youtu' in value):
            # check youtube links with youtu since they might be
            # used with youtu.be our youtube.com links
            res = youtube_id.findall(value)
            if 'list' in value:
                vid_id = res[0] + '?list=' + res[1]
            else:
                vid_id = res[0]
            value = youtube_url + vid_id
            mapping['cloud_url']['youtube'] = vid_id

        elif ('vimeo' in value):
            vimeo = re.compile(r'[\d]{5,}')
            vid_id = vimeo.findall(value)[0]
            value = vimeo_url + vid_id
            cloud = mapping['cloud_url']
            # remove youtube entry if found since youtube macro
            # is before vimeo             
            if cloud.get('youtube'):
                cloud.pop('youtube')
            cloud['vimeo'] = vid_id
        else:
            return "Please enter a video link from Youtube or Vimeo only"

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
        """ check and transform links for video embedding
        """
        res = video_cloud_validator(value, instance)
        if res:
            return res

validation.register(VideoCloudUrlValidator('videoCloudUrlValidator'))
