# -*- coding: utf-8 -*-
from flask import (
    render_template, Blueprint, current_app, request, redirect, flash, url_for,
    jsonify)

from ..mail import send_mail
from .forms import ContactForm
from ..utils import after_app_teardown


index_blueprint = Blueprint('index', __name__,)


def send_contact_mail(data):
    test = data.get('test', '')
    send_mail(
        subject='[CONTACT_FORM]{} message from {}'.format(
            test, data.get('email', '')),
        body=data.get('message'),
        recipients=[current_app.config.get('CONTACT_EMAIL')],
        reply_to=data.get('email', 'unknownemail@example.com'))


@index_blueprint.route('/contact.html')
def contact():
    form = ContactForm()
    return render_template('contact.html', form=form, menu={})


@index_blueprint.route('/')
@index_blueprint.route('/index.html')
def index():
    return render_template('index.html', menu={'select': None})


@index_blueprint.route('/publications.html')
def publications():
    pass


@index_blueprint.route('/contact_form', methods=['GET', 'POST'])
def contact_form():
    data = request.form

    @after_app_teardown
    def send_mail():
        send_contact_mail(data)

    flash('Thank you for your feedback.', 'success')
    return redirect(url_for('.index'))


@index_blueprint.route('/api/minimal_css')
def minimal_css():
    """
    This returns a list of options for the 'above-the-fold' gulp task, that
    creates critical css files.

    Include source code of the following syntax into your jinja templates, in
    order to inject the files:

        {% block above_the_fold_css %}
        {# inject_critical:index.critical.css: #}
        {% endblock above_the_fold_css %}
    """
    criticals = [
        {
            'filename': 'index.critical.css',
            'url': url_for('index.index'),
        }, {
            'filename': 'blog_category.critical.css',
            'url': url_for('blog.category_listing'),
        }, {
            'filename': 'blog.critical.css',
            'url': url_for(
                'blog.blog', category='category-1', slug='first-blog'),
        }]
    return jsonify(list=criticals)

# vim:set ft=python sw=4 et spell spelllang=en:
