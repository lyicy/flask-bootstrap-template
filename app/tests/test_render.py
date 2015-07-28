import pytest
from flask import url_for


class TestFlask(object):

    @pytest.mark.parametrize(
        'url,result',
        [
            ('/', 'Index page'),
            ('/index.html', 'Index page'),
            ('/contact.html', 'Contact form'),
            ('/user/signup.html', 'Sign up'),
            ('/user/login.html', 'Log in to your account'),
            ('/user/forgot_password.html', 'Password forgotten'),
        ],
        ids=[
            'index',
            'index.html',
            'contact',
            'signup',
            'login_render',
            'forgot_password',
        ])
    def test_render_page(self, app, url, result):
        rv = app.get(url, follow_redirects=True)
        assert result in rv.data
        assert rv.status_code == 200

    def test_render_test(self, app):
        rv = app.get('/test')
        assert 'C forward.handle_test' in rv.data

    def test_handle_contact_form(self, app, send_mail, app_ctx):
        """
        actually sends the email, when the command line option
        --send-mail is given
        """
        app.application.config['MAIL_SUPPRESS_SEND'] = send_mail
        target = url_for('index.contact_form')
        rv = app.post(target, data=dict(
            email='jd@example.com',
            message='This is a test message',
            test='[TEST]'), follow_redirects=True)

        if send_mail:
            print("Check that a new test message arrived in the INBOX!")

        assert 'Thank you' in rv.data


# vim:set ft=python sw=4 et spell spelllang=en:
