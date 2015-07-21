# -*- coding: utf-8 -*-

from flask_mail import Message

from flask_blog import mailer
from flask_blog import app
from ..decorators import async


@async
def send_async_email(msg):
    with app.app_context():
        app.logger.info('Sending email...')
        mailer.send(msg)


def send_mail(*args, **kwargs):
    defaults = {
        'sender': (
            'Divine Proportion Pilates', 'mail@divineproportionpilates.com'),
    }
    # test
    defaults.update(kwargs)
    msg = Message(*args, **defaults)
    if app.debug:
        app.logger.info('Sending the following email: {}'.format(msg.body))
    send_async_email(msg)

# vim:set ft=python sw=4 et spell spelllang=en:
