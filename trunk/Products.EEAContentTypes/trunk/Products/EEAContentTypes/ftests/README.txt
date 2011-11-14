Make sure you have have a Zuite object called ftests in your plone site or even better in root of zope. If it's in Plone you can have problem with cached pages. 
In properties of the object enter absolute path to where this directory is located.

To run these tests point your browser to YOUR-INSTANCE-URL/ftests or YOUR-CMS-INSTANCE-URL/ftests

Type in ../testWWW.html to test the public site and ../testCMS.html to test CMS functions and press GO. Then you can press PLAY-all or PLAY-selected in the top right frame and lean back and enyou. If you get any red lines, the test have failed. If it fails on a verifyText line it is probably because the content has changed and the tests need to be updated. 

You NEED to login into the CMS before running the tests.

NOTE: if a link is absolute and points to other domain then the one you started your tests from it will break the test and all following since javascript is not allowed to access information in pages from other domains.
NOTE: keep Captcha test last in the suits as they will fail if you run tests from inside EEA
