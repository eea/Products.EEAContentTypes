from Products.CMFCore.utils import getToolByName

class SKOS(object):
    """ Browser view for generating a SKOS feed from an ATTopic. """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def concepts(self):
        synTool = getToolByName(self.context, 'portal_syndication')

        max = self.request.get('size', None)
        if max is None:
            default_max = synTool.getMaxItems()
            max = synTool.getMaxItems(self.context)
            max = type(max) == type(1) and max or default_max
        else:
            max = int(max)

        brains = self.context.queryCatalog(sort_limit=max)[:max]
        objs = [brain.getObject() for brain in brains]
        objects = [obj for obj in objs if obj is not None]

        concepts = []
        for obj in objects:
            # get all translations that are available for this object
            # translations are of the form { language: [object, wf_state] }
            languages = obj.getTranslations()

            prefLabels = []
            for lang, obj_list in languages.items():
                prefLabel = {'language': lang,
                             'title': obj_list[0].Title() }
                prefLabels.append(prefLabel)

            concept = {'url': obj.absolute_url(),
                       'prefLabels': prefLabels,
                       'definition': obj.Description() }
            concepts.append(concept)

        return concepts
