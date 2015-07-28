# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
from flask import (Flask)
from flask_mail import Mail
from flask.ext.login import LoginManager
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CsrfProtect

from . import config

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


mailer = Mail(app)
mongo = MongoClient(app.config['MONGO_URI'])
db = mongo.get_database(app.config['MONGO_DATABASE'])

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

app.register_blueprint(index_blueprint)
app.register_blueprint(forward_blueprint)
app.register_blueprint(user_blueprint)


def init_db():
    models.create_all_collections()


def drop_db():
    db.client.drop_database(app.config['MONGO_DATABASE'])


if __name__ == '__main__':
    app.run()

# vim:set ft=python sw=4 et spell spelllang=en:
