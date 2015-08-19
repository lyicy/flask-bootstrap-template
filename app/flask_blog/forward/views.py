# -*- coding: utf-8 -*-
import datetime
import os

from flask import (
    send_from_directory, Blueprint, current_app, render_template, request)
from flask_blog import app


forward_blueprint = Blueprint('forward', __name__,)


@forward_blueprint.route('/bower_components/<path:path>')
def bower(path):
    return send_from_directory(
        os.path.join(current_app.config['ROOT'], 'bower_components'), path)


@forward_blueprint.route('/static_gen/<path:path>')
def static_gen(path):
    return send_from_directory(
        os.path.join(current_app.config['ROOT'], '.tmp', 'static_gen'), path)


@forward_blueprint.route('/' + app.config['GOOGLE_SITE_VERIFICATION'])
def handle_google_search_tool():
    return render_template(
        'site-verification.html',
        site_verification=app.config['GOOGLE_SITE_VERIFICATION'])


@forward_blueprint.route('/the-time')
def the_time():
    cur_time = str(datetime.now())
    return cur_time + ' is the current time!  ...YEAH!'


@forward_blueprint.route('/test')
def handle_test():
    return render_template('test.html', menu={})


@forward_blueprint.route('/robots.txt')
def robots_txt():
    if request.host.startswith('next'):
        return "\n".join(["User-agent: *", "Disallow: /"])
    else:
        return "\n".join(["User-agent: *", "Allow: /"])


# vim:set ft=python sw=4 et spell spelllang=en:
