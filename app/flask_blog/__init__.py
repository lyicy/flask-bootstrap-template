# -*- coding: utf-8 -*-
import os
from flask import (Flask)
from flask_mail import Mail
from flask.ext.login import LoginManager
from flask.ext.debugtoolbar import DebugToolbarExtension
from flask.ext.sqlalchemy import SQLAlchemy
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
db = SQLAlchemy(app)
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
from exercises.views import exercise_blueprint
from user.views import user_blueprint

app.register_blueprint(index_blueprint)
app.register_blueprint(forward_blueprint)
app.register_blueprint(exercise_blueprint)
app.register_blueprint(user_blueprint)


def init_db():
    db.create_all()


def drop_db():
    db.drop_all()


if __name__ == '__main__':
    app.run()

# vim:set ft=python sw=4 et spell spelllang=en:
