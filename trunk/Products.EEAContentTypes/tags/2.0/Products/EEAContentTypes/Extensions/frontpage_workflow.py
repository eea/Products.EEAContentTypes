# -*- coding: utf-8 -*-
#
# File: EEAContentTypes.py
#
# Copyright (c) 2006 by []
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'


from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.EEAContentTypes.config import *

##code-section create-workflow-module-header #fill in your manual code here
##/code-section create-workflow-module-header


productname = 'EEAContentTypes'

def setupfrontpage_workflow(self, workflow):
    """Define the frontpage_workflow workflow.
    """
    # Add additional roles to portal
    portal = getToolByName(self,'portal_url').getPortalObject()
    data = list(portal.__ac_roles__)
    for role in ['Editor', 'WebReviewer', 'Manager']:
        if not role in data:
            data.append(role)
    portal.__ac_roles__ = tuple(data)

    workflow.setProperties(title='frontpage_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['new', 'published', 'webqa_pending', 'retracted', 'content_pending', 'proof_reading']:
        workflow.states.addState(s)

    for t in ['retract', 'enable', 'publish', 'submit', 'reject']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Access contents information')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('new')

    ## States initialization

    stateDef = workflow.states['new']
    stateDef.setProperties(title="""New""",
                           transitions=['submit'])
    stateDef.setPermission('View',
                           0,
                           ['Manager', 'Owner', 'Editor'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner', 'Editor'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager', 'Owner', 'Editor'])

    stateDef = workflow.states['published']
    stateDef.setProperties(title="""Published""",
                           transitions=['retract'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])

    stateDef = workflow.states['webqa_pending']
    stateDef.setProperties(title="""Pending (web QA)""",
                           transitions=['reject', 'publish'])
    stateDef.setPermission('View',
                           0,
                           ['Manager', 'Owner', 'WebReviewer', 'Reviewer', 'Editor'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'WebReviewer'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager', 'Owner', 'WebReviewer', 'Reviewer', 'Editor'])

    stateDef = workflow.states['retracted']
    stateDef.setProperties(title="""Retracted""",
                           transitions=['enable', 'publish'])
    stateDef.setPermission('View',
                           0,
                           ['Manager', 'Owner', 'Reviewer', 'Editor'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager', 'Owner', 'Reviewer', 'Editor'])

    stateDef = workflow.states['content_pending']
    stateDef.setProperties(title="""Pending (content review)""",
                           transitions=['submit', 'reject'])
    stateDef.setPermission('View',
                           0,
                           ['Manager', 'Owner', 'WebReviewer', 'Reviewer', 'Editor'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Reviewer'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager', 'Owner', 'WebReviewer', 'Reviewer', 'Editor'])

    stateDef = workflow.states['proof_reading']
    stateDef.setProperties(title="""Pending (Proof reading)""",
                           transitions=['reject', 'submit'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Reviewer'])

    ## Transitions initialization

    transitionDef = workflow.transitions['retract']
    transitionDef.setProperties(title="""Retract""",
                                new_state_id="""retracted""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Retract""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager'},
                                )

    transitionDef = workflow.transitions['enable']
    transitionDef.setProperties(title="""enable""",
                                new_state_id="""new""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""enable""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner; Editor'},
                                )

    transitionDef = workflow.transitions['publish']
    transitionDef.setProperties(title="""Publish""",
                                new_state_id="""published""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Publish""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['submitForWebQA']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.frontpage_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['submit']
    transitionDef.setProperties(title="""Submit""",
                                new_state_id="""proof_reading""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""submitForWebQA""",
                                actbox_name="""Submit""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Reviewer'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['reject']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.frontpage_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['reject']
    transitionDef.setProperties(title="""reject""",
                                new_state_id="""new""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""reject""",
                                actbox_name="""reject""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Owner;Manager;WebReviewer'},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="""""",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="""""",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="""""",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="""""",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="""""",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization


    # WARNING: below protected section is deprecated.
    # Add a tagged value 'worklist' with the worklist name to your state(s) instead.

    ##code-section create-workflow-setup-method-footer #fill in your manual code here
    ##/code-section create-workflow-setup-method-footer



def createfrontpage_workflow(self, id):
    """Create the workflow for EEAContentTypes.
    """

    ob = DCWorkflowDefinition(id)
    setupfrontpage_workflow(self, ob)
    return ob

addWorkflowFactory(createfrontpage_workflow,
                   id='frontpage_workflow',
                   title='frontpage_workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

