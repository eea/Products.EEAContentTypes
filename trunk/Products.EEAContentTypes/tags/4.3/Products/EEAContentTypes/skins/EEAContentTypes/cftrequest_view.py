##bind container=container

return container.REQUEST.RESPONSE.redirect( container.absolute_url() + '/cftrequest_confirmation')
