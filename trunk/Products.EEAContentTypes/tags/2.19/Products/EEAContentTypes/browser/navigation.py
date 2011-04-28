class NavigationHeader(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.subsite_logo = self._logo()

    def logoUrl(self):
        if self.subsite_logo:
            return self.subsite_logo.absolute_url()
        else:
            return None

    def logoLinkUrl(self):
        if self.subsite_logo:
            parent = self.subsite_logo.aq_inner.aq_parent
            return parent.absolute_url()
        else:
            return None

    def shouldDisplayLogo(self):
        return self.subsite_logo is not None

    def _logo(self):
        # rely on acquisition to find a logo in path
        logo = getattr(self.context, 'subsite-logo', None)
        return logo
