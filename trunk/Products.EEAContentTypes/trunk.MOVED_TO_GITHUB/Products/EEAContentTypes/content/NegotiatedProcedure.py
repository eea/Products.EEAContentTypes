""" NegotiatedProcedure """
from Products.Archetypes.atapi import registerType

from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.CallForInterest import CallForInterest
from Products.EEAContentTypes.content.CallForInterest \
    import CallForInterest_schema


class NegotiatedProcedure(CallForInterest):
    """ Negotiated Procedure
    """
    # This name appears in the 'add' box
    archetype_name = 'NegotiatedProcedure'

    meta_type = 'NegotiatedProcedure'
    portal_type = 'NegotiatedProcedure'
    typeDescription = "NegotiatedProcedure"
    typeDescMsgId = 'description_edit_negotiatedprocedure'
    schema = CallForInterest_schema


registerType(NegotiatedProcedure, PROJECTNAME)
