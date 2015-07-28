# -*- coding: utf-8 -*-
import random
import os
from flask import (
    session, render_template, Blueprint, abort, jsonify, redirect, url_for)
from flask.ext.login import login_required, current_user

from . import read_configuration, list_exercises, get_title

from flask_blog import db

blog_blueprint = Blueprint('blog', __name__,)


@blog_blueprint.route('/blog/<category>/<slug>')
def blog(category, slug):
    pass


@blog_blueprint.route('/blog/<category>')
def category_listing(category):
    pass


@blog_blueprint.route('/api/reload/<slug>')
@login_required
def api_reload_blog(slug=k):
    l = list_exercises()
    slugs = [os.path.splitext(e)[0] for e in l]
    return jsonify(slugs=slugs)

# vim:set ft=python sw=4 et spell spelllang=en:
