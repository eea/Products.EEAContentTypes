""" Version widget
"""
from zope.component import queryAdapter
from eea.themecentre.interfaces import IThemeTagging
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.widgets.widget import Widget as AbstractWidget

class Widget(AbstractWidget):
    """ Current themes
    """
    widget_type = 'eeathemetags'
    widget_label = 'EEA theme tags'
    view_js = '++resource++Products.EEAContentTypes.faceted.themes.view.js'
    edit_js = '++resource++Products.EEAContentTypes.faceted.themes.edit.js'
    view_css = '++resource++Products.EEAContentTypes.faceted.themes.view.css'
    edit_css = '++resource++Products.EEAContentTypes.faceted.themes.edit.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = AbstractWidget.edit_schema

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
