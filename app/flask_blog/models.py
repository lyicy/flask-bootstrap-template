import csv
import datetime

from bson.objectid import ObjectId
from flask import current_app, url_for, render_template
from flask.ext.login import UserMixin
from .mail import send_mail
from copy import deepcopy
import itsdangerous

from flask_blog import db, app
from utils import after_app_teardown
from pymongo import IndexModel, ASCENDING


serializer = itsdangerous.URLSafeSerializer(
    secret_key=app.config['SECRET_KEY'])
ACTIVATION_SALT = app.config['ACTIVATION_SALT']  # bytes(urandom(10))


def get_activation_hash(user):
    return serializer.dumps(str(user._id), salt=ACTIVATION_SALT)


class MongoBase(object):

    _id = None

    def getter(self, key):
        return self.values[key]

    def setter(self, key, value):
        self.values[key] = value

    def __getattr__(self, key):
        if key in self.values:
            return self.values[key]
        else:
            raise AttributeError()

#    def __init__(self):
#        for key in self.default.iterkeys():
#            setattr(self, key, property(self.getter, self.setter, None))

    @classmethod
    def create_collection(self):
        db.create_collection(self.collection)

        collection = self._get_collection()
        collection.create_indexes(self.indices)

    @classmethod
    def _get_collection(self):
        return db.get_collection(self.collection)

    def insert(self):
        assert not self._id

        collection = self._get_collection()
        res = collection.insert_one(self.values)
        self._id = res.inserted_id

    def update(self, update):
        assert self._id

        collection = self._get_collection()
        collection.update_one({'_id': self._id}, update)

        # if res.modified_count != 1:
        #    raise RuntimeError(
        #        'Could not update value in collection {}'
        #        .format(str(collection)))


def create_all_collections():
    for cls in [MongoUser]:
        cls.create_collection()


class MongoUser(MongoBase, UserMixin):

    collection = 'users'

    indices = [
        IndexModel([('username', ASCENDING)], unique=True, sparse=True),
        IndexModel([('email', ASCENDING)], unique=True)
        ]

    default = {
        'username': None,
        'name': None,
        'email': None,
        'password': None,
        'registered_on': None,
        'paid': False,
        'wants_newsletter': True,
        'email_validated': False,
        'authenticated': False
    }

    def __init__(self, _id=None, **kwargs):

        MongoBase.__init__(self)

        self.values = deepcopy(self.default)

        if _id:
            self._id = _id
            self.values.update(**kwargs)

        else:
            self.registered_on = datetime.datetime.now()

            self.values.update(**kwargs)

    @classmethod
    def from_email(cls, email):
        collection = cls._get_collection()
        user = collection.find_one({'email': email})
        if user:
            return MongoUser(**user)
        else:
            return None

    @classmethod
    def from_username_or_email(cls, user):
        collection = cls._get_collection()
        user = collection.find_one(
            {'$or': [{'email': user}, {'username': user}]})
        if user:
            return MongoUser(**user)
        else:
            return None

    @classmethod
    def from_id(cls, stringid):
        id = ObjectId(stringid)
        collection = cls._get_collection()
        user = collection.find_one({'_id': id})
        if user:
            return MongoUser(**user)
        else:
            return None

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self._id)

    def as_dict(self):
        return self.values

    def send_activation_email(self, next=None, forgot_password=False):
        activation_hash = get_activation_hash(self)

        target = url_for(
            'user.activation',
            activation_hash=activation_hash,
            next=next,
            _external=True)

        if forgot_password:
            template = 'password_reset_email.txt'
            subject = (
                '''Password reset on your '{}' account.'''
                .format(current_app.config['TITLE']))

        else:
            template = 'activation_email.txt'
            subject = (
                '''Activate your '{}' account!'''
                .format(current_app.config['TITLE']))

        activation_email = render_template(
            template, next=next,
            user=self, target=target)
        send_mail(
            subject=subject, body=activation_email,
            recipients=[(self.name, self.email)])

    def authentication_change(self, value):
        self.update({'$set': {'authenticated': value}})
        self.values['authenticated'] = value

    def set_password(self, value, authentication_change=None):
        if authentication_change is not None:
            update = {'authenticated': authentication_change}
            self.values['authenticated'] = authentication_change
        else:
            update = {}
        update.update({'password': value or ''})
        self.update({'$set': update})
        self.values['password'] = value

    def email_validation_change(self, value):
        self.update({'$set': {'email_validated': value}})
        self.values['email_validated'] = value

    def __repr__(self):
        return 'name {} username {} email {}'.format(
            *[getattr(self, key) for key in ['name', 'username', 'email']])


class Users(object):

    @classmethod
    def save_to_text_file(cls, user):
        with open(current_app.config['EMAILS'], 'a') as fh:
            row = [user.name, user.email]
            writer = csv.writer(fh)
            writer.writerow(row)

    @classmethod
    def add(cls, activate=True, **kwargs):
        user = MongoUser(**kwargs)
        user.insert()
        if activate:
            @after_app_teardown
            def send_activation():
                user.send_activation_email(
                    next=kwargs.get('next', url_for('index.index')))

        cls.save_to_text_file(user)
        return user

    @classmethod
    def from_email(cls, email):
        return MongoUser.from_email(email=email)

    @classmethod
    def from_username_or_email(cls, user):
        return MongoUser.from_username_or_email(user)

    @classmethod
    def from_id(cle, user_id):
        return MongoUser.from_id(stringid=user_id)

# vim:set ft=python sw=4 et spell spelllang=en:
