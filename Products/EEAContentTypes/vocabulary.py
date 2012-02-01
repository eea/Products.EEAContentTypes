""" Vocabularies
"""

vocabs = {
  'themes': (
    ('default', 'Default'),
    ('air', 'Air pollution'),
    ('biodiversity', 'Biodiversity'),
    ('chemicals', 'Chemicals'),
    ('climate', 'Climate change'),
    ('coasts_seas', 'Coasts and seas'),
    ('economy', 'Green economy'),
    ('energy', 'Energy'),
    ('fisheries', 'Fisheries'),
    ('households', 'Households consumption'),
    ('human', 'Environment and health'),
    ('industry', 'Industry'),
    ('landuse', 'Industry'),
    ('natural', 'Natural resources'),
    ('noise', 'Noise'),
    ('other_issues', 'Various other issues'),
    ('policy', 'Policy instruments'),
    ('regions', 'Specific regions'),
    ('scenarios', 'Environmental scenarios'),
    ('soil', 'Soil'),
    ('technology', 'Environmental technology'),
    ('tourism', 'Tourism'),
    ('urban', 'Urban environment'),
    ('waste', 'Waste and material resources'),
    ('water', 'Water'),
),
  'countries': (
    ('default', 'Select your country'),
    ('AND','ANDORRA'),
    ('AUT','AUSTRIA'),
    ('BLR','BELARUS'),
    ('BEL','BELGIUM'),
    ('BIH','BOSNIA AND HERZEGOWINA'),
    ('BGR','BULGARIA'),
    ('HRV','CROATIA (local name: Hrvatska)'),
    ('CYP','CYPRUS'),
    ('CZE','CZECH REPUBLIC'),
    ('DNK','DENMARK'),
    ('SLV','EL SALVADOR'),
    ('EST','ESTONIA'),
    ('FJI','FIJI'),
    ('FIN','FINLAND'),
    ('FRA','FRANCE'),
    ('GEO','GEORGIA'),
    ('DEU','GERMANY'),
    ('GRC','GREECE'),
    ('GRL','GREENLAND'),
    ('HUN','HUNGARY'),
    ('ISL','ICELAND'),
    ('IRL','IRELAND'),
    ('ITA','ITALY'),
    ('LVA','LATVIA'),
    ('LTU','LITHUANIA'),
    ('LUX','LUXEMBOURG'),
    ('MKD','THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA,'),
    ('MLT','MALTA'),
    ('MEX','MEXICO'),
    ('MCO','MONACO'),
    ('NLD','NETHERLANDS'),
    ('NOR','NORWAY'),
    ('POL','POLAND'),
    ('PRT','PORTUGAL'),
    ('ROM','ROMANIA'),
    ('RUS','RUSSIAN FEDERATION'),
    ('SVK','SLOVAKIA (Slovak Republic)'),
    ('SVN','SLOVENIA'),
    ('ESP','SPAIN'),
    ('SWE','SWEDEN'),
    ('CHE','SWITZERLAND'),
    ('TUR','TURKEY'),
    ('GBR','UNITED KINGDOM'),
    ('ZZZ','Other'),
)}

from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
ratios = [
    (u"16:9", "16:9 image ratio"),
    (u"4:3", "4:3 image ratio") ]

ratio_terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                                                  for pair in ratios ]

imageRatioVocabulary = SimpleVocabulary(ratio_terms)

resolutions = [
    (u"1024x600",  "1024x600 WSVGA resolution"),
    (u"1280x720",  "1280x720 16:9 resolution"),
    (u"1366x768",  "1366x768 16:9 resolution"),
    (u"1920x1080", "1920x1080 16:9 resolution")]

res_terms = [ SimpleTerm(value=pair[0], token=pair[0], title=pair[1])
                                            for pair in resolutions]

imageResolutionVocabulary = SimpleVocabulary(res_terms)
