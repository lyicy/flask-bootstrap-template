import os
import csv
import datetime

from sqlalchemy import or_
from flask import current_app, url_for, render_template
from flask.ext.login import UserMixin
from .mail import send_mail

from flask_blog import db


class User(db.Model, UserMixin):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(100), unique=False)
    activation_hash = db.Column(db.String(60), nullable=True, default=None)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200), nullable=True, default=None)
    registered_on = db.Column(db.DateTime, nullable=False)
    paid = db.Column(db.Boolean, nullable=False, default=False)
    wants_newsletter = db.Column(db.Boolean, nullable=False, default=True)
    watched_exercises = db.Column(db.Integer, nullable=False, default=0)
    only_full_product = db.Column(db.Boolean, nullable=False, default=False)
    only_for_dvd = db.Column(db.Boolean, nullable=False, default=False)
    email_validated = db.Column(db.Boolean, nullable=False, default=False)
    authenticated = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(
            self, name, email,
            username=None, password=None,
            wants_newsletter=True, only_for_dvd=False,
            only_full_product=False):
        self.email = email
        if username:
            self.username = username
        else:
            self.username = email
        self.name = name
        self.registered_on = datetime.datetime.now()
        if password:
            self.password = password
        self.wants_newsletter = wants_newsletter
        self.only_for_dvd = only_for_dvd
        self.only_full_product = only_full_product

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def send_activation_email(self, next=None, forgot_password=False):
        self.activation_hash = os.urandom(29).encode('hex')
        db.session.commit()
        target = url_for(
            'user.activation',
            uid=self.id,
            activation_hash=self.activation_hash,
            next=next,
            _external=True)

        if forgot_password:
            activation_email = render_template(
                'password_reset_email.txt', next=next,
                user=self, target=target)
            send_mail(
                subject=(
                    '''Password reset on your '{}' account.'''
                    .format(current_app.config['TITLE'])),
                body=activation_email,
                recipients=[(self.name, self.email)])
        else:
            activation_email = render_template(
                'activation_email.txt', next=next,
                user=self, target=target)
            send_mail(
                subject=(
                    '''Activate your '{}' account!'''
                    .format(current_app.config['TITLE'])),
                body=activation_email,
                recipients=[(self.name, self.email)])

    def __repr__(self):
        return 'name {} username {} email {}'.format(
            self.name, self.username, self.email)


class Users(object):

    @classmethod
    def save_to_text_file(cls, user):
        with open(current_app.config['EMAILS'], 'a') as fh:
            row = [user.name, user.email]
            writer = csv.writer(fh)
            writer.writerow(row)

    @classmethod
    def add(cls, activate=True, **kwargs):
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        if activate:
            user.send_activation_email(
                next=kwargs.get('next', url_for('exercises.exercises')))

        cls.save_to_text_file(user)
        return user

    @classmethod
    def from_email(cls, email):
        return User.query.filter_by(email=email).first()

    @classmethod
    def from_username_or_email(cls, user):
        return User.query.filter(
            or_(User.email == user, User.username == user)).first()

    @classmethod
    def from_id(cle, user_id):
        return User.query.filter_by(id=int(user_id)).first()

# vim:set ft=python sw=4 et spell spelllang=en:
