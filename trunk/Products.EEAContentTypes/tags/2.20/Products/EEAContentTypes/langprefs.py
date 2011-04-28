# It was requested to have the Plone UI in english for logged in staff
# members. Therefore we register a lang prefs method that has higher
# priority than the one found in LanguageTool.
from AccessControl import getSecurityManager
from Products.PlacelessTranslationService.Negotiator import registerLangPrefsMethod

class PrefsForPTS:

    def __init__(self, context):
        pass

    def getPreferredLanguages(self):
        user = getSecurityManager().getUser()
        if user.has_role('Authenticated'):
            return ['en', 'en']
        return None

registerLangPrefsMethod({'klass':PrefsForPTS, 'priority':101 })
