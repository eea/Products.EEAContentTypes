""" Admin
"""
from Products.Five.browser import BrowserView
from Products.CMFPlone.utils import getToolByName

class BaseReorder(object):
    """Abstract class for reordering resources"""

    resource_type = ""
    title = ""

    def __call__(self):

        if not self.request.form.get("save"):
            return self.index()

        url = self.context.absolute_url() + ('/@@reorder_%s' %
                                             self.resource_type)
        resources = self.request.form.get("resources")

        if not resources:
            self.context.plone_utils.addPortalMessage(u'No resources specified')
            return self.request.response.redirect(url)

        util = getToolByName(self.context, "portal_%s" % self.resource_type)
        result = []
        for _i, res_id in enumerate(resources.split("\n")):
            res = util.getResource(res_id.strip())
            result.append(res)


        util.resources = tuple(result)
        util.cookResources()

        self.context.plone_utils.addPortalMessage(u'Resources rearranged')
        return self.request.response.redirect(url)

    @property
    def resources(self):
        """ Resources
        """
        util = getToolByName(self.context, "portal_%s" % self.resource_type)
        res = [r.getId() for r in util.resources]
        return res


class ReorderCSS(BrowserView, BaseReorder):
    """Reorder CSS view"""

    title = "Reorder CSS resources"
    resource_type = "css"

    def __call__(self):
        return BaseReorder.__call__(self)


class ReorderJavascript(BrowserView, BaseReorder):
    """Reorder Javascript view"""

    title = "Reorder Javascript resources"
    resource_type = "javascripts"

    def __call__(self):
        return BaseReorder.__call__(self)
