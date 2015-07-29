# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
from flask import (Flask, g)
from flask_mail import Mail
from flask.ext.login import LoginManager
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CsrfProtect
from werkzeug.local import LocalProxy

from . import config
from blog import Blog

earoot = os.environ.get('FLASK_BLOG_ROOT', None)
if earoot:
    app_cfg = {
        'template_folder': os.path.join(earoot, 'templates'),
        'static_folder': os.path.join(earoot, 'static'),
    }
else:
    app_cfg = {}

app = Flask(__name__, **app_cfg)
CsrfProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)

app.debug = False

config.configure_app(app)

config.configure_logger(app)

login_manager.login_view = 'user.login'


blog_cache = Blog()
blog_cache.init_app(app)

mailer = Mail(app)


def get_database_connection():
    con = getattr(g, 'database_connection', None)
    if con is None:
        g.con = con = MongoClient(app.config['MONGO_URI'])
        g.db = con.get_database(app.config['MONGO_DATABASE'])
    return g.db


@app.teardown_appcontext
def close_database_connection(error=None):
    if error is None:
        callbacks = getattr(g, 'on_teardown_callbacks', ())
        for callback in callbacks:
            callback()

    con = getattr(g, 'database_connection', None)
    if con is not None:
        con.close()

db = LocalProxy(get_database_connection)

toolbar = DebugToolbarExtension(app)

from . import models


@login_manager.user_loader
def load_user(user_id):
    return models.Users.from_id(user_id)

##############
# blueprints #
##############

from index.views import index_blueprint
from forward.views import forward_blueprint
from user.views import user_blueprint
from blog.views import blog_blueprint

app.register_blueprint(index_blueprint)
app.register_blueprint(forward_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(blog_blueprint)


def init_db():
    models.create_all_collections()


def drop_db():
    db.client.drop_database(app.config['MONGO_DATABASE'])


if __name__ == '__main__':
    app.run()

# vim:set ft=python sw=4 et spell spelllang=en:
