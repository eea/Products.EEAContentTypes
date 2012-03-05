return """
<script>
    close_dialog('%s');
</script>
""" % context.REQUEST.form.get('_active_region');
