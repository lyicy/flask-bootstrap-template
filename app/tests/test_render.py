import pytest
from flask import url_for


class TestFlask(object):

    @pytest.mark.parametrize(
        'url,result',
        [
            ('index.index', 'slowly but steadily'),
            ('index.contact', 'Contact form'),
            ('blog.category_listing', 'All blogs'),
            (
                ('blog.category_listing', {'category': 'category-2'}),
                'Category 2'),
            (
                (
                    'blog.blog',
                    {'category': 'category-1', 'slug': 'first-blog'}),
                'First post'),
            ('user.signup', 'Sign up'),
            ('user.login', 'Log in to your account'),
            ('user.forgot_password', 'Password forgotten'),
        ],
        ids=[
            'index',
            'contact',
            'blog_list',
            'blog_category2',
            'blog_first_post',
            'signup',
            'login_render',
            'forgot_password',
        ])
    def test_render_page(self, cli, url, result):
        with cli.application.app_context():
            if type(url) == tuple:
                endpoint, kwargs = url
                target = url_for(endpoint, **kwargs)
            else:
                target = url_for(url)
        rv = cli.get(target, follow_redirects=True)
        assert result in rv.data
        assert 'canonical.example.com' in rv.data
        assert rv.status_code == 200

    @pytest.mark.parametrize(
        'url,result',
        [
            ('index.minimal_css', 'index.critical'),
        ],
        ids=[
            'minimal_css',
        ])
    def test_render_api(self, cli, url, result):
        with cli.application.app_context():
            if type(url) == tuple:
                endpoint, kwargs = url
                target = url_for(endpoint, **kwargs)
            else:
                target = url_for(url)
        rv = cli.get(target, follow_redirects=True)
        assert result in rv.data
        assert rv.status_code == 200

    def test_render_test(self, cli):
        rv = cli.get('/test')
        assert 'C forward.handle_test' in rv.data

    def test_handle_contact_form(self, cli, send_mail, app_ctx):
        """
        actually sends the email, when the command line option
        --send-mail is given
        """
        cli.application.config['MAIL_SUPPRESS_SEND'] = send_mail
        target = url_for('index.contact_form')
        rv = cli.post(target, data=dict(
            email='jd@example.com',
            message='This is a test message',
            test='[TEST]'), follow_redirects=True)

        if send_mail:
            print("Check that a new test message arrived in the INBOX!")

        assert 'Thank you' in rv.data


# vim:set ft=python sw=4 et spell spelllang=en:
