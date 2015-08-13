#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask.ext.script import Manager

import flask_blog
from flask_blog import app, config

config.configure_app(app)

manager = Manager(app)


@manager.command
def init_db():
    flask_blog.init_db()


@manager.command
def drop_db():
    flask_blog.drop_db()


@manager.command
def test():
    import pytest
    errno = pytest.main('tests')
    sys.exit(errno)


if __name__ == '__main__':
    manager.run()

# vim:set ft=python sw=4 et spell spelllang=en:
