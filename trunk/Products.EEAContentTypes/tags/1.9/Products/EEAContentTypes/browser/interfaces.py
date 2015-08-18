from zope.interface import Interface
from zope.schema import TextLine

class IRSSShare(Interface):

    def main():
        """ Returns objects for the main rss share. It takes all frontpage
        items and items from rssrecipes. With arguements exclude_channels and
        include_channels you can choose which rssrecipe to exclude and include.
        Default include list is all and exclude none.
        The old highlights.rdf. """

class ICFTRegistration(Interface):

    def hasCanceled():
        """ return true if user has canceled registration """

    def canView():
        """ Returns true if the provided cftrequestor exists or a Manager is
            viewing the cft. """

    def getAwardNotice():
        """ Return true if there has been published a award notice. """

class IOrganisation(Interface):

    def validData():
        """ return xml data status """

    def getLastUpdated():
        """ return modification time of eeastaff.xml """

    def getOrgData(org, title, manager):
        """ return employees for a organisation. Default is all org
            and none managers. """

    def getOrgUnits(orgs):
        """ return org data for each org in orgs. """

    def getManager(org):
        """ return manager for an organisation. """

    def getOrganisations():
        """ return organisation list """

    def getDirector():
        """ return the director """

    def getDeputyDirector():
        """ return the deputy director """

    def getStaffList(org):
        """ return all employees or employees of one org in dict form
            { 'first_name' : '',
              'last_name' : '',
              'email' : '',
              'job_title' : '',
              'programme' : '' } """

class IRelatedThemes(Interface):

    def getRelatedThemes():
        """ Fetch themes for the current object and return a dict with
            theme name, id, url to theme. """

class IFrontPageHighlights(Interface):

    def getHigh():
        """ Return the published highlights with visibility `top` and that
            haven't expired. Sort by publish date and return the number
            that is configured in portal_properties.frontpage_properties.
        """

    def getMedium():
        """ Return highlights with visibility `middle` and the ones with
            `top` that are left over because of the configuration in
            portal_properties.frontpage_properties. """

    def getLow():
        """ return the published highlights with visibility bottom. """

    def getPromotions():
        """ Return all published promotions and group them in categories.
            Categories are defined by the folders containing the promotions. """
            
    def getHighArticles():
        """ Return the published articles with visibility `top` and that
            haven't expired. Sort by publish date and return the number
            that is configured in portal_properties.frontpage_properties.
        """
    def getMediumArticles():
        """ Return the published articles with visibility `middle` and that
            haven't expired. Sort by publish date and return the number
            that is configured in portal_properties.frontpage_properties.
        """

    def getLowArticles():
        """ Return the published articles with visibility `bottom` and that
            haven't expired. Sort by publish date and return the number
            that is configured in portal_properties.frontpage_properties.
        """

class IPromotionCategory(Interface):

    def getPromotions():
        """ Return published promotions in this group. """

class IQuickEvent(Interface):

    def hasCanceled():
        """ return true if user has canceled submition """

    def canView():
        """ Returns true if the event is published. """

    def step2():
        """ Handle confirmation or correction of event. """

class ILanguages(Interface):

    def getTranslationLanguages():
        """ Return languages for translation. """

    def getTranslatedSitesLanguages():
        """ Return languages for translated sites.  """

class IEmployee(Interface):
    """ employee information for rdf synchronization from intranet. """

    first_name = TextLine( title=u'First name',
                           description=u'',
                           required = True )
    last_name = TextLine( title=u'Last name',
                           description=u'',
                           required=True )
    personnelNb = TextLine( title=u'Personnel number',
                            description=u'',
                            required=True)
    email = TextLine( title=u'Email',
                      description=u'',
                      required=True)
    employment_start = TextLine( title=u'Employment start',
                                 description=u'',
                                 required=True)
    employment_end = TextLine( title=u'Employment end',
                               description=u'',
                               required=True)
    job_title = TextLine( title=u'Job title',
                          description=u'',
                          required=True)
    organisation_code = TextLine( title=u'Organisation code',
                                  description=u'',
                                  required=True)
    organisation_name = TextLine( title=u'Organisation name',
                                  description=u'',
                                  required=True)
    manager = TextLine( title=u'manager',
                        description=u'',
                        required=True)

class IDocumentRelated(Interface):
    def bottom_media():
        pass

    def feeds():
        pass

    def mediacount():
        pass

    def multimedia():
        pass

    def pages():
        pass

    def other():
        pass

    def top_count():
        pass

    def top_media():
        pass

class IAutoRelated(Interface):

    def sameTheme():
        """ return related documents of the same type. Relation is by theme. """

    def autoContext():
        """ return related items in a specific order: manually tagged, same theme, latest items."""

    def sameType():
        """ return related documents of the same type. Relation is by type. """

    def sameTypeByTheme():
        """ return related documents of the same type. Grouped by theme. """

    def sameTypeByPublicationGroup():
        """ return related doucments of the same type, grouped by publication group. """

class IGeoConverter(Interface):
    def geoConvert():
        """ """

class IGeoMapData(Interface):
    pass

class IGeoMapView(Interface):
    pass

class IGeoPositionView(Interface):
    pass

class IGoogleEarthView(Interface):
    pass

class IURL(Interface):

    def object_url(brain=None):
        """ Return the URL which should be used to view the object """
    
    def listing_url(brain=None):
        """ Return the URL that represents the URL in a listing """

    def is_external():
        """ Does this object point to an external URL? """

    def css_class():
        """ Returns a class name that should be present in anchor links """