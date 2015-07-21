import pytest
import flask_blog
import flask_blog.index.views
from flask_blog import models


class TestFlask(object):

    @pytest.mark.parametrize(
        'url,result',
        [
            ('/', 'Essential Activity'),
            ('/index.html', 'Essential Activity'),
            ('/thankyou.html', 'Thank you'),
            ('/faq.html', 'Health issues'),
            ('/pricing.html', '59'),
            ('/aboutbethany.html', 'Bethany Drohmann'),
            ('/contact.html', 'Contact us'),
            ('/user/signup.html', 'Sign up'),
            ('/user/newsletter.html', 'Sign up'),
            ('/user/login.html', 'Log in to your account'),
            ('/user/forgot_password.html', 'Password forgotten'),
        ],
        ids=[
            'index',
            'index.html',
            'thankyou',
            'faq',
            'pricing',
            'aboutbethany',
            'contact',
            'signup',
            'newsletter',
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

    def test_cta(self, app_tmpdir):
        test_emails, _, app = app_tmpdir
        test_emails.write('hello world\n')
        flask_blog.init_db()

        rv = app.post(
            'form.html',
            data=dict(
                name='John Doe',
                email='jd@gmail.com',
            ),
            follow_redirects=True)

        assert 'hello world' in test_emails.read()
        assert 'John Doe,jd@gmail.com' in test_emails.read()
        assert 'Thank you' in rv.data
        entries = models.User.query.all()
        assert entries[0].name == 'John Doe'

        rv = app.post(
            '/form.html',
            data=dict(
                name='John Doe',
                email='jd@gmail.com',
            ),
            follow_redirects=True)

        assert 'Email already registered' in rv.data

    def test_cta_incorrect(self, app):
        flask_blog.init_db()

        rv = app.post(
            '/form.html',
            data=dict(
                name='',
                email='invalid',
            ), follow_redirects=True)

        assert 'This field is required' in rv.data
        assert 'Invalid email address' in rv.data

    def test_read_faq(self, ctx):
        res = flask_blog.index.views.read_faq(flask_blog.app)
        assert 'Health issues' in res

    def test_handle_contact_form(self, app):
        app.application.config['MAIL_SUPPRESS_SEND'] = False
        rv = app.post('/contact_form', data=dict(
            email='mdrohmann@gmail.com',
            message='This is a test message',
            test='[TEST]'), follow_redirects=True)

        print("Check that a new test message arrived in the INBOX!")

        assert 'Thank you' in rv.data


# vim:set ft=python sw=4 et spell spelllang=en:
