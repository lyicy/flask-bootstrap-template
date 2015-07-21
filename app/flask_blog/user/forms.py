# -*- coding: utf-8 -*-
from flask_wtf import Form
from wtforms import StringField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from .. import models


class NewPasswordForm(Form):
    password = PasswordField(
        'Password', validators=[
            DataRequired(),
            EqualTo('confirm', 'Passwords need to match.'),
            Length(
                min=6, max=30,
                message='Password needs to have at least %(min)d characters')
        ])
    confirm = PasswordField(
        'Confirmation', validators=[DataRequired()])


class NoPasswordForm(Form):
    user = StringField(
        'Username or email', validators=[DataRequired()])


class LoginForm(Form):
    """
    form for the login dialog.

    Note, that the validation happens in the view function, because we do not
    want to load the user twice from the database.
    """

    user = StringField(
        'Username or email', validators=[DataRequired()])
    password = PasswordField(
        'Password', validators=[DataRequired()])


class TrialSignupForm(Form):

    name = StringField(
        'Name', validators=[DataRequired()])
    email = StringField(
        'Email Address', validators=[DataRequired(), Email()])
    update_for_full_product = BooleanField('update-for-full-product')
    only_for_dvd = BooleanField('only-for-dvd')

    def validate(self):
        initial_validation = super(TrialSignupForm, self).validate()
        if not initial_validation:
            return False

        user = models.Users.from_email(self.email.data)
        if user:
            self.email.errors.append("Email already registered")
            return False

        return True
# vim:set ft=python sw=4 et spell spelllang=en:
