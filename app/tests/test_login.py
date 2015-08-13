# -*- coding: utf-8 -*-

from bson.objectid import ObjectId
from flask import url_for
import pytest
import flask_blog
from flask_blog import models

# Fixtures


@pytest.fixture()
def not_logged_in_user(cli, mongodb_inited, app_ctx):
    """ Fixture for a user that is not logged in """

    with flask_blog.app.test_request_context():
        user = models.Users.add(
            name='John Doe',
            email='jd@example.com')

    assert not user.is_authenticated()

    return cli, user


@pytest.fixture
def verified_user(not_logged_in_user):
    """ fixture for a verified user """
    return test_verify_email(not_logged_in_user)


@pytest.fixture
def logged_in_user(not_logged_in_user):
    """ fixture for a user that is logged in with a verified email address """
    return test_set_password_after_email_verification(not_logged_in_user)


@pytest.fixture
def user_with_password(logged_in_user):
    """
    fixture for a user who is not logged in, but has a password (activated
    email)
    """
    return test_logout(logged_in_user)


# Test pages, that only work for logged-in users:

class TestAuthentication(object):
    urls = ['/admin']
    results = ['Administration']
    ids = ['admin']

    @pytest.mark.parametrize(
        'url,result',
        zip(urls, results),
        ids=ids)
    def test_logged_in_render_page(self, logged_in_user, url, result):
        cli, _ = logged_in_user
        rv = cli.get(url, follow_redirects=True)
        assert result in rv.data
        assert rv.status_code == 200

    @pytest.mark.parametrize('url', urls, ids=ids)
    def test_login_required(self, not_logged_in_user, url):
        cli, _ = not_logged_in_user
        rv = cli.get(url, follow_redirects=False)
        assert rv.status_code == 302


def test_verify_email(not_logged_in_user):
    """ test verification of email through click on activation link """

    cli, user = not_logged_in_user
    activation_hash = models.get_activation_hash(user)

    assert not user.email_validated
    rv = cli.get(
        '/user/activate/{}'.format(activation_hash),
        follow_redirects=True)

    user = models.Users.from_email('jd@example.com')
    assert user.email_validated
    assert not user.is_authenticated()

    assert 'Email address is verified' in rv.data
    assert 'Please select a password' in rv.data
    return cli, user


def test_activation_unsafe_nexturl(not_logged_in_user):
    """ check that the activation email does not re-direct to invalid urls """
    cli, user = not_logged_in_user
    activation_hash = models.get_activation_hash(user)
    rv = cli.post(
        ("""/user/activate/{}?next=http://evilphish.com/"""
         .format(activation_hash)),
        data=dict(password='irrelevant', confirm='irrelevant'),
        follow_redirects=True)
    assert rv.status_code == 400


def test_too_short_password(not_logged_in_user):
    """ password test 1: too short password """
    cli, user = not_logged_in_user
    activation_hash = models.get_activation_hash(user)
    rv = cli.post(
        '/user/activate/{}'.format(activation_hash),
        data=dict(password='sec', confirm='sec'),
        follow_redirects=True)

    assert 'Password needs to have at least 6 characters' in rv.data


def test_set_password_after_email_verification(not_logged_in_user):
    """ set password successfully after activation of account """

    cli, user = not_logged_in_user
    activation_hash = models.get_activation_hash(user)
    assert not user.email_validated
    assert not user.password

    rv = cli.get('/user/login_required', follow_redirects=False)
    assert rv.status_code == 302

    rv = cli.post(
        '/user/activate/{}'.format(activation_hash),
        data=dict(password='secret', confirm='secret'),
        follow_redirects=True)

    rv = cli.get('/user/login_required', follow_redirects=False)
    assert 'John Doe' in rv.data

    user = models.Users.from_id(user._id)
    assert user.password
    assert user.is_authenticated()
    assert user.registered_on is not None
    assert user.email_validated
    return cli, user


def test_login_invalid_user(mongodb_inited, cli):
    """
    invalid login attempt
    """

    with cli.application.app_context():
        target = url_for('user.login')

    rv = cli.post(
        target,
        data=dict(user='nonexistent', password='secret'),
        follow_redirects=True)

    assert 'Invalid username' in rv.data


def test_login_no_password(verified_user):
    """
    login attempt of a user without a password.
    """

    cli, user = verified_user

    rv = cli.post(
        '/user/login.html',
        data=dict(user=user.email, password='does not matter'),
        follow_redirects=True)

    assert 'Set a password' in rv.data
    assert 'There is no password associated' in rv.data


def test_login_invalid_password(user_with_password):
    """
    login attempt with an invalid password.
    """

    cli, user = user_with_password

    rv = cli.post(
        '/user/login.html',
        data=dict(user=user.email, password='invalid'),
        follow_redirects=True)

    assert 'Invalid password' in rv.data


def test_login_success(user_with_password):
    """
    Successful re-login
    """
    cli, user = user_with_password

    assert not user.is_authenticated()

    cli.post(
        '/user/login.html',
        data=dict(user=user.email, password='secret'),
        follow_redirects=True)

    user = models.Users.from_id(user._id)
    assert user.is_authenticated()


def test_name_email_creates_unvalidated_user(cli, mongodb_inited):
    """
    Test of the registration page.

    This is the registration process.  People will not need to set a password
    at this point.
    """
    cli.post(
        'user/signup.html',
        data=dict(
            name='John Doe',
            email='jd@example.com',
            wants_newsletter=True,
        ),
        follow_redirects=True)

    user = models.Users.from_email('jd@example.com')
    assert user
    assert not user.paid
    assert user.wants_newsletter
    assert not user.email_validated
    assert user.is_authenticated
    # TODO: We might want to change this later...?
    assert user.is_active


def test_providing_existing_email(cli, mongodb_inited):
    """
    Registration with an existing email.
    """

    with flask_blog.app.test_request_context():
        models.Users.add(
            name='John Dorian',
            email='jd@example.com')

    rv = cli.post(
        'user/signup.html',
        data=dict(
            name='John Doe',
            email='jd@example.com',
        ),
        follow_redirects=True)

    assert 'Email already registered' in rv.data

    user = models.Users.from_email('jd@example.com')
    assert user
    assert not user.is_authenticated()


def test_click_on_invalid_validation_link(not_logged_in_user):
    """
    invalid validation link.
    """

    cli, user = not_logged_in_user
    assert not user.email_validated

    rv_invalid = cli.get(
        '/user/activate/invalid',
        follow_redirects=True)

    assert rv_invalid.status_code == 404

    class FakeUser(object):
        _id = ObjectId('123456789012')

    fake_user = FakeUser()
    activation_hash = models.get_activation_hash(fake_user)
    with cli.application.app_context():
        target = url_for('user.activation', activation_hash=activation_hash)
    rv_invalid = cli.get(
        target,
        follow_redirects=True)

    assert rv_invalid.status_code == 404


@pytest.mark.parametrize(
    'target, result, no_user',
    [('forgot_password.html',
      'We reset your password and sent a re-activation email',
      False),
     ('forgot_password.html',
      'Invalid username or email address',
      True),
     ('no_password.html',
      'We sent a new activation email to your email address',
      False),
     ('no_password.html',
      'Invalid username or email address',
      True),
     ],
    ids=[
        'forgot_success', 'forgot_fail',
        'no_password_success', 'no_password_fail'])
def test_password_forgotten_or_not_existent(
        target, result, no_user, not_logged_in_user):
    """
    If the user forgot her password, or cannot find her activation email.  :(
    """
    cli, user = not_logged_in_user

    if no_user:
        user_data = 'invalid'
    else:
        user_data = user.email

    rv_request = cli.post(
        '/user/{}'.format(target),
        data=dict(
            user=user_data,
        ),
        follow_redirects=True)

    assert result in rv_request.data


@pytest.mark.xfail
def test_change_password(logged_in_user):
    """ change the password in the settings dialog. """
    cli, luser = logged_in_user

    rv = cli.post(
        'user/{}/settings',
        data=dict(
            id=luser._id,
            pass1='newpass',
            pass2='newpass',
            password_change=True),
        follow_redirects=True)

    assert 'Password successfully changed' in rv.data

    user = models.Users.from_id(luser._id)
    assert user.password == 'newpass'


@pytest.mark.xfail
def test_change_password_fail(logged_in_user):
    """
    Passwords do not match error.
    """

    cli, luser = logged_in_user
    old_password = luser.password

    rv = cli.post(
        'user/{}/settings',
        data=dict(
            id=luser._id,
            pass1='pass1',
            pass2='pass2',
            password_change=True,
        ),
        follow_redirects=True)

    assert 'Passwords did not match' in rv.data

    user = models.Users.from_id(luser._id)
    assert user.password == old_password


def test_logout(logged_in_user):
    """
    test that the logout works.
    """

    cli, luser = logged_in_user
    uid = luser._id

    assert luser.is_authenticated()

    rv = cli.get(
        '/user/logout',
        follow_redirects=False)

    assert rv.status_code == 302

    user = models.Users.from_id(uid)
    assert not user.is_authenticated()

    return cli, user


def test_change_email():
    """
    Change the email of a user, and re-verify it.

    Maybe, add a new one?
    """
    pass


def test_account_settings():
    """
    render the account settings.
    """


def test_change_name():
    """
    Change the user name
    """
    pass


def test_buy_something():
    """
    Look into the paypal developer manual to implement this.
    """


# vim:set ft=python sw=4 et spell spelllang=en:
