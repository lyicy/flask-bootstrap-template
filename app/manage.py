#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


from flask_blog import app, db, config

config.configure_app(app)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


@manager.command
def init_db():
    db.create_all()


@manager.command
def drop_db():
    db.drop_all()


@manager.command
def test():
    import pytest
    errno = pytest.main('tests')
    sys.exit(errno)


if __name__ == '__main__':
    manager.run()

# vim:set ft=python sw=4 et spell spelllang=en:
