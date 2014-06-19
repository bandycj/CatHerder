from flask.ext.wtf import Form
from wtforms import StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, Email


__author__ = 'Chris'


class NameForm(Form):
    name = StringField('User Name', validators=[DataRequired()], )

class EmailForm(Form):
    email = EmailField('Email', validators=[DataRequired(), Email()])