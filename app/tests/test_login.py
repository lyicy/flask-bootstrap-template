# -*- coding: utf-8 -*-

import pytest
import flask_blog
from flask_blog import models


@pytest.fixture()
def not_logged_in_user(request, dbapp):

    flask_blog.init_db()
    with flask_blog.app.test_request_context():
        user = models.Users.add(
            name='John Doe',
            email='jd@gmail.com')

    assert not user.is_authenticated()

    return dbapp, user


def test_verify_email(not_logged_in_user):

    app, user = not_logged_in_user
    assert not user.email_validated
    rv = app.get(
        '/user/activate/{}/{}'.format(user.id, user.activation_hash),
        follow_redirects=True)

    user = models.Users.from_email('jd@gmail.com')
    assert user.email_validated
    assert not user.is_authenticated()

    assert 'Email address is verified' in rv.data
    assert 'Please select a password' in rv.data
    return app, user


@pytest.fixture
def verified_user(not_logged_in_user):
    return test_verify_email(not_logged_in_user)


def test_activation_unsafe_nexturl(not_logged_in_user):
    app, user = not_logged_in_user
    rv = app.post(
        ("""/user/activate/{}/{}?next=http://evilphish.com/"""
         .format(user.id, user.activation_hash)),
        data=dict(password='irrelevant', confirm='irrelevant'),
        follow_redirects=True)
    assert rv.status_code == 400


def test_too_short_password(not_logged_in_user):
    app, user = not_logged_in_user
    rv = app.post(
        '/user/activate/{}/{}'.format(user.id, user.activation_hash),
        data=dict(password='sec', confirm='sec'),
        follow_redirects=True)

    assert 'Password needs to have at least 6 characters' in rv.data


def test_set_password_after_email_verification(not_logged_in_user):
    app, user = not_logged_in_user
    assert not user.email_validated
    assert not user.password

    rv = app.get('/user/login_required', follow_redirects=False)
    assert rv.status_code == 302

    rv = app.post(
        '/user/activate/{}/{}'.format(user.id, user.activation_hash),
        data=dict(password='secret', confirm='secret'),
        follow_redirects=True)

    assert 'Your email is verified and you are logged in now.' in rv.data

    rv = app.get('/user/login_required', follow_redirects=False)
    assert 'John Doe' in rv.data

    user = models.Users.from_id(user.id)
    assert user.password
    assert user.is_authenticated()
    assert user.email_validated
    return app, user


@pytest.fixture
def logged_in_user(not_logged_in_user):
    return test_set_password_after_email_verification(not_logged_in_user)


@pytest.fixture
def user_with_password(logged_in_user):
    return test_logout(logged_in_user)


def test_login_invalid_user(dbapp):
    rv = dbapp.post(
        '/user/login.html',
        data=dict(user='nonexistent', password='secret'),
        follow_redirects=True)

    assert 'Invalid username' in rv.data


def test_login_no_password(verified_user):
    app, user = verified_user

    rv = app.post(
        '/user/login.html',
        data=dict(user=user.email, password='does not matter'),
        follow_redirects=True)

    assert 'Set a password' in rv.data
    assert 'There is no password associated' in rv.data


def test_login_invalid_password(user_with_password):
    app, user = user_with_password

    rv = app.post(
        '/user/login.html',
        data=dict(user=user.email, password='invalid'),
        follow_redirects=True)

    assert 'Invalid password' in rv.data


def test_login_success(user_with_password):
    app, user = user_with_password

    assert not user.is_authenticated()

    rv = app.post(
        '/user/login.html',
        data=dict(user=user.email, password='secret'),
        follow_redirects=True)

    assert 'Suggested repetitions' in rv.data

    user = models.Users.from_id(user.id)
    assert user.is_authenticated()


def test_name_email_creates_unvalidated_user(dbapp):
    """
    This is the registration process.  People will not need a password, until
    they buy our stuff.
    """
    app = dbapp

    rv = app.post(
        'user/signup.html',
        data=dict(
            name='John Doe',
            email='jd@gmail.com',
            update_for_full_product=True,
            only_for_dvd=True,
        ),
        follow_redirects=True)

    assert 'Suggested repetitions' in rv.data

    user = models.Users.from_email('jd@gmail.com')
    assert user
    assert not user.paid
    assert user.wants_newsletter
    assert user.only_for_dvd
    assert not user.email_validated
    assert user.is_authenticated
    # TODO: We might want to change this later...?
    assert user.is_active


def test_providing_existing_email(dbapp):
    app = dbapp

    with flask_blog.app.test_request_context():
        models.Users.add(
            name='John Dorian',
            email='jd@gmail.com')

    rv = app.post(
        'user/signup.html',
        data=dict(
            name='John Doe',
            email='jd@gmail.com',
        ),
        follow_redirects=True)

    assert 'Email already registered' in rv.data

    user = models.Users.from_email('jd@gmail.com')
    assert user
    assert not user.is_authenticated()


def test_click_on_invalid_validation_link(not_logged_in_user):
    """
    This is not so important yet.  We'll simply filter out the people, who we
    cannot send their emails to.  But we will need it later to let people set a
    password...
    """

    app, user = not_logged_in_user
    assert not user.email_validated

    rv_invalid = app.get(
        '/user/activate/12/invalid',
        follow_redirects=True)

    assert rv_invalid.status_code == 400


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
    If the user forgot her password. :(
    """
    app, user = not_logged_in_user

    if no_user:
        user_data = 'invalid'
    else:
        user_data = user.email

    rv_request = app.post(
        '/user/{}'.format(target),
        data=dict(
            user=user_data,
        ),
        follow_redirects=True)

    assert result in rv_request.data


@pytest.mark.xfail
def test_change_password(logged_in_user):
    app, luser = logged_in_user

    rv = app.post(
        'user/{}/settings',
        data=dict(
            id=luser.id,
            pass1='newpass',
            pass2='newpass',
            password_change=True),
        follow_redirects=True)

    assert 'Password successfully changed' in rv.data

    user = models.Users.from_id(luser.id)
    assert user.password == 'newpass'


@pytest.mark.xfail
def test_change_password_fail(logged_in_user):
    """
    Should fail.
    """

    app, luser = logged_in_user
    old_password = luser.password

    rv = app.post(
        'user/{}/settings',
        data=dict(
            id=luser.id,
            pass1='pass1',
            pass2='pass2',
            password_change=True,
        ),
        follow_redirects=True)

    assert 'Passwords did not match' in rv.data

    user = models.Users.from_id(luser.id)
    assert user.password == old_password


def test_logout(logged_in_user):
    """ test that the logout works. """

    app, luser = logged_in_user
    uid = luser.id

    assert luser.is_authenticated()

    rv = app.get(
        '/user/logout',
        follow_redirects=False)

    assert rv.status_code == 302

    user = models.Users.from_id(uid)
    assert not user.is_authenticated()

    return app, user


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


@pytest.mark.parametrize(
    'url,result',
    [
        ('/exercise/ten_more', 'Ten more exercises coming soon'),
        ('/exercise/teacups', 'Teacups on Spine'),
        ('/exercise/balloons', 'Balloons'),
        ('/exercises', 'Suggested repetitions'),
    ],
    ids=[
        'ten_more',
        'teacup_exercise',
        'balloons_exercise',
        'list_exercises',
    ])
def test_logged_in_render_page(logged_in_user, url, result):
    app, _ = logged_in_user
    rv = app.get(url, follow_redirects=True)
    assert result in rv.data
    assert rv.status_code == 200

# vim:set ft=python sw=4 et spell spelllang=en:
