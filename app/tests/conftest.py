# -*- coding: utf-8 -*-
import pytest
import os

os.environ['FLASK_BLOG_TESTING'] = 'True'
import flask_blog
from flask_blog import config


def pytest_addoption(parser):
    parser.addoption(
        "--send-mail", action="store_true",
        help="send mail to test the smtp account configuration.")


def pytest_generate_tests(metafunc):
    if 'send_mail' in metafunc.fixturenames:
        metafunc.parametrize(
            "send_mail",
            [metafunc.config.option.send_mail])


@pytest.fixture()
def dbapp(request, app):
    """ database access fixture """
    flask_blog.init_db()

    def clean_db():
        flask_blog.drop_db()

    request.addfinalizer(clean_db)

    return app


@pytest.fixture()
def ctx():
    """ fixture for a test request context """
    ctx = flask_blog.app.test_request_context()
    ctx.push()
    return ctx


@pytest.fixture()
def app():
    """ fake app """
    flask_blog.app.config.from_object(config.TestConfig)
    return flask_blog.app.test_client()


# vim:set ft=python sw=4 et spell spelllang=en:
