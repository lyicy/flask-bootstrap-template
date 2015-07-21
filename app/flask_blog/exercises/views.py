# -*- coding: utf-8 -*-
import random
import os
from flask import (
    session, render_template, Blueprint, abort, jsonify, redirect, url_for)
from flask.ext.login import login_required, current_user

from . import read_configuration, list_exercises, get_title

from flask_blog import db

exercise_blueprint = Blueprint('exercises', __name__,)


@exercise_blueprint.route('/exercise/<slug>')
def exercise(slug):
    try:
        conf = {
            'exercise': read_configuration(
                '{}.yaml'.format(slug), markdown=True)}
    except IOError:
        if slug == 'ten_more':
            l = list_exercises()
            titles = [get_title(e) for e in l]
            slugs = [os.path.splitext(e)[0] for e in l]
            return render_template('ten_more.html', slugs=slugs, titles=titles)
        else:
            abort(404)

    l = list_exercises()

    ind = l.index('{}.yaml'.format(slug))
    #    if (ind + 1) == len(l):
    #        next_exercise = ('ten_more', 'Ten more exercises')
    #    else:
    #        nfile = l[(ind + 1)]
    #        nslug = os.path.splitext(nfile)[0]
    #        next_exercise = (nslug, get_title(nfile))
    #
    #    if (ind - 1) == -1:
    #        prev_exercise = ('ten_more', 'Ten more exercises')
    #    else:
    #        pfile = l[(ind - 1)]
    #        pslug = os.path.splitext(pfile)[0]
    #        prev_exercise = (pslug, get_title(pfile))

    nfile = l[(ind + 1) % (len(l))]
    nslug = os.path.splitext(nfile)[0]
    next_exercise = (nslug, get_title(nfile))
    if current_user.is_anonymous():
        if 'watched_exercises' in session:
            session['watched_exercises'] += 1
        else:
            session['watched_exercises'] = 1
    else:
        current_user.watched_exercises += 1
        db.session.commit()
        session['watched_exercises'] = current_user.watched_exercises

    conf['exercise']['next_exercise'] = next_exercise

    return render_template('exercise.html', **conf)


@exercise_blueprint.route('/exercises')
def exercises():
    # pick an exercise randomly! :)
    l = list_exercises()
    random.shuffle(l)
    exercise = l[0]
    slug = os.path.splitext(exercise)[0]
    return redirect(url_for('exercises.exercise', slug=slug))


@exercise_blueprint.route('/api/exercises')
@login_required
def api_exercises():
    l = list_exercises()
    slugs = [os.path.splitext(e)[0] for e in l]
    return jsonify(slugs=slugs)

# vim:set ft=python sw=4 et spell spelllang=en:
