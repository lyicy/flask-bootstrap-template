# -*- coding: utf-8 -*-

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired, Email


from .. import models


class ContactForm(Form):
    email = TextField(
        'Email Address', validators=[DataRequired(), Email()])
    message = TextField('Message')


class EmailSignupForm(Form):
    name = TextField(
        'Name', validators=[DataRequired()]
    )
    email = TextField(
        'Email Address', validators=[DataRequired(), Email()]
    )

    def validate(self):
        initial_validation = super(EmailSignupForm, self).validate()
        if not initial_validation:
            return False

        user = models.Users.from_email(self.email.data)
        if user:
            self.email.errors.append("Email already registered")
            return False

        return True


# vim:set ft=python sw=4 et spell spelllang=en:
