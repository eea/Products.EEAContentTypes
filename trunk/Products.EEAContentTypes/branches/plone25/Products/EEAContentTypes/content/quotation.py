""" quotation """

from Products.Archetypes.atapi import ( Schema, TextField, RichWidget,
        StringField, StringWidget)

quotation_schema = Schema((

    TextField(
        name='quotationText',
        widget=RichWidget
        (
            label="Quotation text",
            description="Choose a quotation for the content",
            label_msgid="EEAContentTypes_label_quotationtext",
            description_msgid="EEAContentTypes_help_quotationtext",
            i18n_domain="EEAContentTypes",
            rows=10,
        ),
        index="KeywordIndex:brains",
    ),

    StringField(
        name='quotationSource',
        widget=StringWidget
        (
            label="Quotation source",
            description="Choose the source of the quotation",
            label_msgid="EEAContentTypes_label_quotationtext",
            description_msgid="EEAContentTypes_help_quotationtext",
            i18n_domain="EEAContentTypes",
        ),
        index="KeywordIndex:brains",
    ),
))
