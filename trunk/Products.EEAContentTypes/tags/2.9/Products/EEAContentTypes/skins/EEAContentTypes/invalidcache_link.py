##bind context=context
##title=return invalidate cache link

link = '<a href="%s/@@invalidate_cache" rel="nofollow" title="Refresh this page" i18n:attributes="title" i18n:translate="Refresh this page">Refresh this page</a>' % context.absolute_url()

if context.REQUEST.get('HTTP_HOST', '') == 'nohost':
    # testing env cannot execute javascript
    return link
 
return """ <script type="text/javascript">
   // <![CDATA[
       document.write('%s');
       // ]]>
   </script> """ % link
