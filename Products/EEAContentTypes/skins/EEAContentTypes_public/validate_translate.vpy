## Script (Python) "validate_base"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=lp_translating_from, lp_translating_to
##
errors = {}

if lp_translating_from == lp_translating_to:
    message = context.translate(msgid='message_select_different_languages',
                                default='Please select different values '
                                        'for each language.',
                                domain='linguaplone')
    context.plone_utils.addPortalMessage(message, type='error')
    return state.set(status='failure', errors=errors)

errors = context.validate(REQUEST=context.REQUEST, errors=errors, data=1, metadata=0)

if errors:
    # #5302 add errors to the portal message for translation since they don't show up in state
    # 101427 remove errors from top of translation edit form since they
    # now show up within the field render
    context.plone_utils.addPortalMessage('Please correct the indicated errors:', type='error')
    return state.set(status='failure', errors=errors)
else:
    context.plone_utils.addPortalMessage('Changes saved.')
    return state.set()
