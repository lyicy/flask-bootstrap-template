# -*- coding: utf-8 -*-
import pytest
import os
from os import mkdir
from os.path import join as pjoin, exists as pexists
import shutil
from tempfile import mkdtemp
import subprocess
from time import sleep

from pymongo import MongoClient

os.environ['FLASK_BLOG_TESTING'] = 'True'
import flask_blog
from flask_blog import config, init_db, drop_db


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
def app_ctx(request):
    """ fixture for a test request context """
    ctx = flask_blog.app.app_context()
    ctx.push()

    request.addfinalizer(lambda: ctx.pop())
    return ctx


@pytest.fixture()
def ctx():
    """ fixture for a test request context """
    ctx = flask_blog.app.test_request_context()
    ctx.push()
    return ctx


@pytest.fixture()
def cli():
    """ fake client app """
    flask_blog.app.config.from_object(config.TestConfig)
    return flask_blog.app.test_client()


@pytest.fixture(scope='function')
def mongodb_inited(mongodb, request):
    with flask_blog.app.app_context():
        init_db()

    def _drop_db():
        with flask_blog.app.app_context():
            drop_db()

    request.addfinalizer(_drop_db)


@pytest.fixture(scope='session')
def mongodb(request):
    cls = {}
    cls['tempdir'] = mkdtemp('mongo_connection_test')
    db_dir = pjoin(cls['tempdir'], 'db')
    mkdir(db_dir)
    config_file = pjoin(cls['tempdir'], 'config')
    cls['pid_file'] = pjoin(cls['tempdir'], 'mongo.pid')
    cls['log_path'] = pjoin(cls['tempdir'], 'mongo.log')
    with open(config_file, 'w') as fh:
        fh.write('\n'.join([
            'port=27027', 'dbpath={}'.format(db_dir),
            'nojournal=true', 'noprealloc=true']))
    subprocess.check_call([
        'mongod', '-f', config_file,
        '--fork', '--logpath', cls['log_path'],
        '--pidfilepath', cls['pid_file']])

    cls['client'] = MongoClient('mongodb://localhost:27027')

    def cleanup():
        if pexists(cls['pid_file']):
            with open(cls['pid_file'], 'r') as fh:
                pid = fh.read()
            sleep(0.5)
            subprocess.check_call(['kill', pid.strip()])
        shutil.rmtree(cls['tempdir'])

    request.addfinalizer(cleanup)

    return cls

# vim:set ft=python sw=4 et spell spelllang=en:
