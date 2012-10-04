""" Windmil
"""
from windmill.authoring import WindmillTestClient

def test_recordingSuite0():
    """ Tests
    """
    client = WindmillTestClient(__name__)

    client.click(link=u'About EEA')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'What we do', timeout=u'8000')
    client.click(link=u'What we do')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Governance', timeout=u'8000')
    client.click(link=u'Governance')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Countries and Eionet', timeout=u'8000')
    client.click(link=u'Countries and Eionet')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'European Union partners', timeout=u'8000')
    client.click(link=u'European Union partners')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'International cooperation', timeout=u'8000')
    client.click(link=u'International cooperation')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Environmental management at EEA',
                            timeout=u'8000')
    client.click(link=u'Environmental management at EEA')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Documents', timeout=u'8000')
    client.click(link=u'Documents')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Jobs / Vacancies', timeout=u'8000')
    client.click(link=u'Jobs / Vacancies')
    client.waits.forPageLoad(timeout=u'20000')
    client.waits.forElement(link=u'Contract opportunities', timeout=u'8000')
    client.click(link=u'Contract opportunities')
    client.waits.forPageLoad(timeout=u'20000')
