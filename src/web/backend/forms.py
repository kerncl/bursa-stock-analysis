# 3rd Party lib
from flask_wtf import Form
from wtforms import StringField, SubmitField, SelectField
from wtforms import validators


class StockForm(Form):
    company = StringField("Company name")
    company_fullname = StringField("Company Full Name")
    category = SelectField("Category",
                           choices=[('%%', '-'),
                                    ('Construction', 'Construction'),
                                    ('Consumer Products & Services', 'Consumer & Services'),
                                    ('Energy', 'Energy'),
                                    ('Financial Services', 'Finance'),
                                    ('Health Care', 'Health'),
                                    ('Industrial Products & Services', 'Industrial & Services')])
    market = SelectField("Market", choices=[('%%', '-'),
                                            ('Main Market', 'Main'),
                                            ('Ace Market', 'Ace')])
    submit = SubmitField("Search")
    pass