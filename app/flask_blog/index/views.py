# -*- coding: utf-8 -*-
from flask import (
    render_template, Blueprint, current_app, request, redirect, flash, url_for)

from ..mail import send_mail
from .forms import EmailSignupForm, ContactForm
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
    return render_template('contact.html', form=form)


@index_blueprint.route('/')
@index_blueprint.route('/index.html')
def index():
    form = EmailSignupForm()
    return render_template('index.html', form=form)


@index_blueprint.route('/contact_form', methods=['GET', 'POST'])
def contact_form():
    data = request.form

    @after_app_teardown
    def send_mail():
        send_contact_mail(data)

    flash('Thank you for your feedback.', 'success')
    return redirect(url_for('.index'))


# vim:set ft=python sw=4 et spell spelllang=en:
