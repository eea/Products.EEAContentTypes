""" Monkey patches
"""
from ZODB.POSException import ConflictError

def getPathLanguage(self):
    """Checks if a language is part of the current path."""
    if not hasattr(self, 'REQUEST'):
        return []
    domain = self.REQUEST.get('SERVER_URL') + '/'
    path = self.REQUEST.get('ACTUAL_URL')[len(domain):]
    if len(path) == 2 and not path.endswith('/'):
        path += '/'
    try:
        if len(path) > 2 and path.index('/') == 2:
            if path[:2] in self.getSupportedLanguages():
                return path[:2]
    except ConflictError:
        raise
    except Exception:
        pass
    return None
