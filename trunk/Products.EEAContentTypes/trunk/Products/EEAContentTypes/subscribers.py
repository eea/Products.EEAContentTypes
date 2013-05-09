""" Subscribers
"""

def lowercaseKeywords(obj, evt):
    """ Store all keywords lowercase and remove duplicates
    """
    if 'subject' in obj.schema:
        data = obj.schema['subject'].getRaw(obj)
        data = tuple([x.lower() for x in data])
        obj.schema['subject'].getMutator(obj)(tuple(set(data)))
