#The close_dialog() js function is used in 2 circumstances:
#
#1. in indicators aggregated edit, when the parameter is a
#region that needs to be reloaded (the _active_region var is
#just persisted across requests)
#
#2. in the "Create new content type" eea.relations portlet,
#where the parameter is the url of the content item that
#was added


return """
<script>
    close_dialog('%s');
</script>
""" % context.REQUEST.form.get('_active_region', context.absolute_url());
