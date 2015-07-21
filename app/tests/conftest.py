# -*- coding: utf-8 -*-
import pytest
import os

os.environ['EA55_TESTING'] = 'True'
import flask_blog
from flask_blog import config


@pytest.fixture()
def dbapp(request, app):
    flask_blog.init_db()

    def clean_db():
        flask_blog.drop_db()

    request.addfinalizer(clean_db)

    return app


@pytest.fixture()
def ctx():
    ctx = flask_blog.app.test_request_context()
    ctx.push()
    return ctx


@pytest.fixture()
def app():
    flask_blog.app.config.from_object(config.TestConfig)
    return flask_blog.app.test_client()


@pytest.fixture()
def app_tmpdir(tmpdir):
    test_emails = tmpdir.join('test_emails')
    test_db = tmpdir.join('test.sqlite')
    flask_blog.app.config.from_object(config.TestConfig)
    flask_blog.app.config['EMAILS'] = str(test_emails)
    flask_blog.app.config['DATABASE'] = str(test_db)
    flask_blog.app.config['WTF_CSRF_ENABLED'] = False
    flask_blog.app.config['SQLALCHEMY_DATABASE_URI'] = (
        '''sqlite:///{}'''.format(str(test_db)))
    return test_emails, test_db, flask_blog.app.test_client()

# vim:set ft=python sw=4 et spell spelllang=en:
