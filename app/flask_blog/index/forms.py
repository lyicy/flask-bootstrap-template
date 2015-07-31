# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email


class ContactForm(Form):
    email = TextField(
        'Email Address', validators=[DataRequired(), Email()])
    message = TextField('Message')


# vim:set ft=python sw=4 et spell spelllang=en:
