# 3rd Party lib
from flask_wtf import Form
from wtforms import StringField, SubmitField
from wtforms import validators


class StockForm(Form):
    company = StringField("Company name")
    company_fullname = StringField("Company Full Name")
    category = StringField("Category")
    market = StringField("Market")
    submit = SubmitField("Search")
    pass