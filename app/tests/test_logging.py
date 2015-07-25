# test SMTPLogger handler

import os
from flask_blog import app


def test_smtp_logger(send_mail):
    if not os.getenv('FLASK_BLOG_SETTINGS', ''):
        return

    if app.config.get('LOGGER_MAIL', False) and send_mail:
        app.logger.error(
            'This is a test error from the test_smtp_logger_test')
        print ('Check that you received a logging email in your inbox')

# vim: set ft=python sw=4 et spell spelllang=en:
