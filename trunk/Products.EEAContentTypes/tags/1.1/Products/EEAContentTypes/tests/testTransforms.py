from Testing import ZopeTestCase
from Products.EEAContentTypes.config import *
from Products.EEAContentTypes.tests.base import EEAContentTypeTestCase
from Products.EEAContentTypes.transforms import ProtectEmail
from Products.EEAContentTypes.browser.organisation import emailjs
from Products.PortalTransforms.data import datastream

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

class TestTransforms(EEAContentTypeTestCase):
    """Test-cases for transforms. """


    def afterSetUp(self):
        EEAContentTypeTestCase.afterSetUp(self)
        self.pt = self.portal.portal_transforms

    def test_protectEmail(self):
        transformer = ProtectEmail()
        data = datastream('data')
        orig = """ <p> Some HTML with an email@domain.com that will be protected</p> """
        answer = """ <p> Some HTML with an 
<script type="text/javascript">
   document.write(create_contact_info_local('email','domain.com','email at domain.com') + '');
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
 that will be protected</p> """
        data = transformer.convert(orig, data)
        self.failUnless( str(data) == answer, data)
        data = datastream('data')
        orig = """ <p> Some HTML with an `email title &lt;email@domain.com&gt;`__ that will be protected</p> """
        data = transformer.convert(orig, data)        
        answer = """ <p> Some HTML with an 
<script type="text/javascript">
   document.write(create_contact_info_local('email','domain.com','email title'));
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
 that will be protected</p> """
        self.failUnless( str(data) == answer, data)

        data = datastream('data')
        orig = """ <p> Some HTML with an `email title &lt;email@domain.com&gt;`__ that will be protected and this email@domain2.com too.</p> """
        data = transformer.convert(orig, data)        
        answer = """ <p> Some HTML with an 
<script type="text/javascript">
   document.write(create_contact_info_local('email','domain.com','email title'));
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
 that will be protected and this 
<script type="text/javascript">
   document.write(create_contact_info_local('email','domain2.com','email at domain2.com') + '');
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
 too.</p> """
        self.failUnless( str(data) == answer, data)


        data = datastream('data')
        orig = """ <p>And those french` use and the `re :(  Some HTML with an `email title &lt;email@domain.com&gt;`__ that will be protected and this <a href="mailto:email.lastname@domain2.com?Subject=something">too email</a> and a <a href="mailto:email.lastname@domain2.eu.com?Subject=something">too email</a>.</p> """
        data = transformer.convert(orig, data)        
        answer = """ <p>And those french` use and the `re :(  Some HTML with an 
<script type="text/javascript">
   document.write(create_contact_info_local('email','domain.com','email title'));
</script>
<noscript>
   <em>Email Protected.<br />
   Please enable JavaScript.</em>
</noscript>
 that will be protected and this <a href="mailto:email.lastname@domain2.com?Subject=something">too email</a> and a <a href="mailto:email.lastname@domain2.eu.com?Subject=something">too email</a>.</p> """
        self.failUnless( str(data) == answer, data)

        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTransforms))
    return suite


if __name__ == '__main__':
    framework()

        
