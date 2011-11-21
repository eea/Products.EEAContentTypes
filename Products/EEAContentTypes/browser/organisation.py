""" Organisation
"""
from App.Common import package_home
from DateTime import DateTime
from Products.CMFCore.exceptions import ResourceLockedError
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.EEAContentTypes.browser.interfaces import IOrganisation, IEmployee
from rdflib.Graph import ConjunctiveGraph
from rdflib.Namespace import Namespace
from rdflib.StringInputSource import StringInputSource
from zope.schema import getFieldNames
import logging
import os
import sys
import urllib2
import zope.interface
logger = logging.getLogger('Products.EEAContentTypes.browser.organisation')


def breakNameIfToLong(name, length=13, where='-'):
    """ Break name
    """
    name = name.replace(' - Deputy Director', '')
    if len(name) > length:
        if name.find(where) > -1:
            newWhere = '%s\n' % where
            return name.replace(where, newWhere)
    return name


def getOnlyOrgName(orgPath):
    """ Org name
    """
    orgNameIdx = orgPath.rfind('/') + 1
    return orgPath[ orgNameIdx:]


def isHeadOfProgramme(org):
    """ Head of programme
    """
    for k in range(10):
        if str(k) in org:
            return False
    return True


def prepareStaffNumber(data):
    """ Staff number
    """
    total = 0
    for k in data.keys():
        if not isHeadOfProgramme(k):
            data[k[:3]] += data[k]
    for k in data.keys():
        if isHeadOfProgramme(k):
            total += data[k]
    data['total'] = total
    return data


emailjs = """
<script type="text/javascript">
   document.write(create_contact_info_local('%s','%s','%s'));
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
"""

emailjs_dot = """
<script type="text/javascript">
   document.write(create_contact_info_local('%s','%s','%s') + '%s');
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
"""


class UpdateStaffList(BrowserView):
    """ Update staff list
    """
    def update(self):
        """ Update
        """
        rdf = urllib2.urlopen(self.context.url).read()
        self.context.setModificationDate(DateTime())
        self.context.setFile(rdf)


class UpdateOrganigram(BrowserView):
    """ Update organigram
    """

    def update(self):
        """ Update
        """
        props = getToolByName(self.context, 'portal_properties', None)
        staff_props = getattr(props, 'eeastaff_properties')
        eeastaff_fs = staff_props.getProperty('eeastaff_fs', '')
        eeastaff_cms = staff_props.getProperty('eeastaff_cms', '')

        # get EEAStaff data
        products_path = os.path.dirname(
            os.path.dirname(package_home(globals())))
        try:
            fs_data = open(os.path.join(
                os.path.dirname(products_path), eeastaff_fs), 'rb')
            fs_data = fs_data.read()
        except Exception, err:
            fs_data = ''
            logger.exception(err)

        # upload data
        plone_ob = self.context.unrestrictedTraverse(eeastaff_cms, None)
        if plone_ob:
            if plone_ob.wl_isLocked():
                raise ResourceLockedError, "File is locked via WebDAV"
            if fs_data.strip():
                plone_ob.update_data(fs_data, 'text/xml', len(fs_data))
                plone_ob.setEffectiveDate(DateTime())


class RDF2Employee(object):
    """ RDF to employee
    """
    zope.interface.implements(IEmployee)

    first_name = u''
    last_name = u''
    personnelNb = u''
    email = u''
    employment_start = u''
    employment_end = u''
    job_title = u''
    organisation_code = u''
    organisation_name = u''
    manager = u''

    NS = Namespace('http://intranet.eea.eu.int/inhousedir/staff-ns/1.0/')

    def __init__(self, empInfo):
        fieldNSmapping = {}
        for fieldName in getFieldNames(IEmployee):
            fieldNSmapping[self.NS[fieldName]] = fieldName
        # predicate, object
        for p, o in empInfo:
            fieldName = fieldNSmapping.get(p, None)
            if fieldName:
                setattr(self, fieldName, o.encode('utf8'))

    def __getitem__(self, key):
        return getattr(self, key, '')

    def __str__(self):
        result = ''
        for fieldName in getFieldNames(IEmployee):
            result += '%s: %s\n' % (fieldName, getattr(self, fieldName))
        return result

    def items(self):
        """ Items
        """
        return [ (key, getattr(self, key, '')) for
                 key in getFieldNames(IEmployee) ]


class Organisation(BrowserView):
    """ Organisation
    """
    zope.interface.implements(IOrganisation)

    def __init__(self, context, request):
        super(Organisation, self).__init__(context, request)
        if getattr(context, 'portal_type', 'No Archetype') not in [
            'File', 'ATFile', 'No Archetype']:
            self.context = context.unrestrictedTraverse('eeastaff', None)

        self.validDatas = True
        self._rdf = None
        self._employees = []

    @property
    def rdf(self):
        """ RDF
        """
        if self._rdf:
            return self._rdf

        data = self.context
        if not hasattr(data, 'read'):
            if callable(data.data):
                data = StringInputSource(data.data())
            else:
                data = StringInputSource(data.data)

        try:
            self._rdf = ConjunctiveGraph().parse(data)
        except Exception:
            self.context.error_log.raising(sys.exc_info())
            self.validDatas = False
            self._rdf = ConjunctiveGraph()
        return self._rdf

    @property
    def employees(self):
        """ Employees
        """
        if not self._employees:
            self._employees = [
                emp for emp in
                self.rdf.subjects(RDF2Employee.NS['first_name'])]
        return self._employees

    def validData(self):
        """ Valid data
        """
        return self.validDatas

    def getLastUpdated(self):
        """ Last updated
        """
        return self.context.getEffectiveDate()

    def getOrgData(self, org, title=None, manager=None, main=0):
        """ Org data
        """
        managers = []
        result = []
        employees = [
            empId for empId, orgCode in
            self.rdf.subject_objects(RDF2Employee.NS['organisation_code'])
            if self._checkOrgCode(org, orgCode)
        ]

        for empId in employees:
            emp = RDF2Employee(list(self.rdf.predicate_objects(empId)))

            if title is not None and not title in emp.job_title.lower():
                continue

            if emp.manager == '1':
                managers.append(emp)
            else:
                result.append(emp)
        if manager is not None:
            if manager == '1':
                result = managers
            managers = []
        result = managers + result
        return self._prepareData(result, org, main)

    def getManagers(self):
        """ Managers
        """
        return

    def getOrganisations(self):
        """ Organisations
        """
        orgs = {}
        orgs_info = {}
        res = {'orgs': [], 'orgs_info': {}, 'orgs_names': {}}
        for empId, orgCode in self.rdf.subject_objects(
            RDF2Employee.NS['organisation_code']):
            emp = RDF2Employee(list(self.rdf.predicate_objects(empId)))
            orgCode = getOnlyOrgName(orgCode)
            if isHeadOfProgramme(orgCode):
                orgs[orgCode] = emp.organisation_name
            orgs_info[orgCode] = orgs_info.get(orgCode, 0) + 1
            if orgCode[0] == '/':
                orgCode = orgCode[-3:]
            else:
                orgCode = orgCode[:3]

        res['orgs_names'] = orgs
        res['orgs'].extend(orgs.keys())
        res['orgs'].sort()
        res['orgs_info'] = prepareStaffNumber(orgs_info)
        return res

    def _checkOrgCode(self, org, orgcode):
        """ Org code
        """
        res = False
        if org.upper() == 'EDO':
            if ('EDO/EDO' in orgcode) or (len(orgcode) == 13):
                res = True
        else:
            if org in orgcode:
                res = True
        return res

    def _prepareData(self, data, org, main=0):
        """ Data
        """
        orgs = []
        orgnames = []
        for res in data:
            org_code = str(res['organisation_code'])
            org_code = org_code[ org_code.find(org): ]
            orgname = getOnlyOrgName(res['organisation_code'])
            res_jobTitle = res['job_title']
            #if res_jobTitle == 'Executive Director':
            #    res_jobTitle = 'Head of programme'
            if main and org_code.endswith(org):
                result = {
                    'orgname' : orgname,
                    'last_name' : breakNameIfToLong(res['last_name']),
                    'first_name' :  breakNameIfToLong(res['first_name']),
                    'empid' : res['personnelNb'],
                    'organisation_name' :  res['organisation_name'],
                    'job_title' : breakNameIfToLong(res_jobTitle, where='/'),
                    'manager' : int(res['manager'])
                }
                return [ result ]
            elif not main and org_code.startswith(org):
                if orgname not in orgnames:
                    orgnames.append(orgname)
                    orgs.append({
                        'orgname' : orgname,
                        'last_name' : breakNameIfToLong(res['last_name']),
                        'first_name' :  breakNameIfToLong(res['first_name']),
                        'empid' : res['personnelNb'],
                        'organisation_name' :  res['organisation_name'],
                        'job_title' : breakNameIfToLong(
                            res_jobTitle, where='/'),
                        'manager' : int(res['manager']) })
        orgs.sort(lambda x, y : cmp(x['orgname'], y['orgname']))
        return orgs

    def getStaffList(self, org=None):
        """ Staff list
        """
        result = []
        employees = [
            empId for empId, _orgCode in
            self.rdf.subject_objects(RDF2Employee.NS['organisation_code'])
        ]

        for empId in employees:
            name = ''
            domain = ''
            employee = RDF2Employee(list(self.rdf.predicate_objects(empId)))
            org_name = getOnlyOrgName(employee['organisation_code'])

            emp = dict(employee.items())
            emp['programme'] = '%s - %s' % (
                org_name, employee['organisation_name'])
            if employee['email'].find('@') > 0:
                name, domain = employee['email'].split('@')
            emp['email'] = emailjs % (name, domain, 'Email')
            emp['org_name'] = org_name
            result.append(emp)
        result.sort(lambda x, y: cmp(x['first_name'], y['first_name']))
        return result


    def getDirector(self):
        """ Director
        """
        return self.getManager(org='EDO', title='executive director')

    def getDeputyDirector(self):
        """ Deputy director
        """
        return self.getManager(org='GAN', title='deputy director')

    def getManager(self, org='EDO', title=None):
        """ Manager
        """
        result = self.getOrgData(org, title, manager='1', main=1)
        if len(result) > 0:
            return result[0]
        return None

    def getOrgUnits(self, orgs=None):
        """ Org units
        """
        if orgs is None:
            orgs = []
        units = []
        if len(orgs) == 0:
            props = getToolByName(self.context, 'portal_properties', None)
            staff_props = getattr(props, 'eeastaff_properties')
            orgs = staff_props.getProperty('organisations', [])

        for org in orgs:
            units.append(self.getOrgData(org))
        return units

