""" Subscribers
"""
import logging

logger = logging.getLogger('EEAContentTypes.subscribers')

def lowercaseKeywords(obj, evt):
    """ Store all keywords lowercase and remove duplicates
    """
    try:
        schema = obj.schema
    except AttributeError:
        schema = obj.context.schema
        obj = obj.context
    except Exception:
        return

    try:
        if 'subject' in schema:
                data = schema['subject'].getRaw(obj)
                data = tuple([x.lower() for x in data])
                schema['subject'].getMutator(obj)(tuple(set(data)))
    except Exception:
        logger.info('Skipped lowercase keywords')
