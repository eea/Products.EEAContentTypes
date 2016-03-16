""" CallForProposal """
from Products.Archetypes.atapi import registerType

from Products.EEAContentTypes.config import PROJECTNAME
from Products.EEAContentTypes.content.CallForInterest import CallForInterest
from Products.EEAContentTypes.content.CallForInterest \
    import CallForInterest_schema


class CallForProposal(CallForInterest):
    """Call for proposal
    """
    # This name appears in the 'add' box
    archetype_name = 'CallForProposal'

    meta_type = 'CallForProposal'
    portal_type = 'CallForProposal'
    typeDescription = "CallForProposal"
    typeDescMsgId = 'description_edit_negotiatedprocedure'
    schema = CallForInterest_schema


registerType(CallForProposal, PROJECTNAME)
