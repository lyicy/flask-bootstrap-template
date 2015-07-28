# -*- coding: utf-8 -*-

from passlib.hash import bcrypt
from flask import (
    Blueprint, request, redirect, render_template,
    url_for, flash, abort, current_app)
from flask.ext.login import (
    login_required, logout_user, login_user, current_user)
from .forms import (
    TrialSignupForm, LoginForm, NoPasswordForm, NewPasswordForm)
import itsdangerous

from flask_blog import models
from ..utils import redirect_back, is_safe_url, after_app_teardown

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/user/logout')
@login_required
def logout():
    current_user.authentication_change(False)

    logout_user()
    flash('You are logged out now! Thank you for visiting.', 'success')
    return redirect(url_for('index.index'))


@user_blueprint.route('/user/newsletter.html', methods=['GET', 'POST'])
def interest():
    form = TrialSignupForm(request.form)
    if form.validate_on_submit():

        models.Users.add(
            activate=False,
            name=form.name.data,
            email=form.email.data,
            wants_newsletter=True,
            only_full_product=form.update_for_full_product.data,
            only_for_dvd=form.only_for_dvd.data)

        flash(
            'Thank you for your interest in {}'
            .format(current_app.config['TITLE']), 'success')

        return redirect(url_for('index.thankyou'))
    return render_template('newsletter.html', form=form)


@user_blueprint.route('/user/signup.html', methods=['GET', 'POST'])
def signup():
    form = TrialSignupForm(request.form)
    if form.validate_on_submit():

        user = models.Users.add(
            name=form.name.data,
            email=form.email.data,
            wants_newsletter=form.wants_newsletter.data)

        user.authentication_change(True)

        # ## ATTENTION:  Currently the user is logged in right after sign up.
        login_user(user)

        flash('You are logged in now.', 'success')
        flash(
            'If you want to log in from a different computer, '
            'activate your account with the activation email, we '
            'sent to you.', 'info')

        return redirect(url_for('index.index'))
    return render_template('signup.html', form=form)


@user_blueprint.route('/user/login.html', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():

        user = models.Users.from_username_or_email(form.user.data)

        if not user:
            form.user.errors.append('Invalid username or email.')
            return render_template('login.html', form=form)

        if not user.password:
            flash('There is no password associated with your account.  '
                  'Please activate it by clicking on the link in your '
                  'activation email.', 'error')
            return redirect(
                url_for(
                    'user.no_password',
                    next=request.args.get('next')))

        if bcrypt.verify(
                form.password.data, user.password):
            user.authentication_change(True)
            login_user(user)
            flash('You are successfully logged in.  Welcome!', 'success')
            return redirect_back('index.index')
        else:
            form.password.errors.append('Invalid password')
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@user_blueprint.route('/user/forgot_password.html', methods=['GET', 'POST'])
def forgot_password():
    form = NoPasswordForm(request.form)

    if form.validate_on_submit():

        user = models.Users.from_username_or_email(form.user.data)

        if not user:
            form.user.errors.append('Invalid username or email address.')
            return render_template('forgot_password.html', form=form)

        user.set_password(None)

        @after_app_teardown
        def send_activation():
            user.send_activation_email(
                next=request.args.get('next'), forgot_password=True)

        flash(
            'We reset your password and sent a re-activation email to '
            'your email address.', 'success')
        return redirect_back('user.login')

    return render_template('forgot_password.html', form=form)


@user_blueprint.route('/user/no_password.html', methods=['GET', 'POST'])
def no_password():
    form = NoPasswordForm(request.form)
    if form.validate_on_submit():

        user = models.Users.from_username_or_email(form.user.data)

        if not user:
            form.user.errors.append('Invalid username or email address.')
            return render_template('no_password.html', form=form)

        @after_app_teardown
        def send_activation():
            user.send_activation_email(next=request.args.get('next'))

        flash(
            'We sent a new activation email to your email address.', 'success')

        return redirect_back('index.index')

    return render_template('no_password.html', form=form)


@user_blueprint.route('/user/login_required')
@login_required
def test_login_required():
    return repr(current_user)


@user_blueprint.route(
    '/user/activate/<activation_hash>',
    methods=['GET', 'POST'])
def activation(activation_hash):
    form = NewPasswordForm(request.form)

    try:
        uid = models.serializer.loads(
            activation_hash, salt=models.ACTIVATION_SALT)
    except itsdangerous.BadSignature:
        abort(404)

    user = models.Users.from_id(uid)

    if not user:
        flash('Could not validate the request', 'error')
        abort(404)

    user.email_validation_change(True)

    if user.password:
        next = request.args.get('next')
        if not is_safe_url(next):
            abort(400)

        next = next or url_for('index.index')

        return render_template(
            'activation_with_password.html', next=next)

    if form.validate_on_submit():

        user.set_password(bcrypt.encrypt(form.password.data), True)

        login_user(user)

        return redirect(
            url_for(
                'user.activation',
                activation_hash=activation_hash,
                **request.args))

    next = request.args.get('next')
    return render_template(
        'activation_no_password.html',
        uid=uid, activation_hash=activation_hash, next=next, form=form)


@user_blueprint.route('/user/settings')
def settings():
    pass


@user_blueprint.route('/admin')
@login_required
def admin():
    """ dummy function to test a login_required call """
    return render_template('admin.html')

# vim:set ft=python sw=4 et spell spelllang=en:
