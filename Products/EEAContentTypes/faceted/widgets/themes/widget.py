""" Version widget
"""
from zope.component import queryAdapter
from zope.browserpage.viewpagetemplatefile import ViewPageTemplateFile

from eea.themecentre.interfaces import IThemeTagging
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget


class Widget(AbstractWidget):
    """ Current themes
    """
    widget_type = 'eeathemetags'
    widget_label = 'EEA theme tags'

    index = ViewPageTemplateFile('widget.pt')

    @property
    def themes(self):
        """ Themes
        """
        tagging = queryAdapter(self.context, IThemeTagging)
        if not tagging:
            return []
        return tagging.tags

    def query(self, form):
        """ Add theme to query
        """
        query = {}
        value = self.themes
        if not value:
            return query

        query['getThemes'] = {'query': value, 'operator': 'and'}
        return query
