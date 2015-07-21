# -*- coding: utf-8 -*-

from threading import Thread
from flask_blog import app


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        try:
            thr.start()
        except Exception as e:
            app.logger.error(str(e.message))

    return wrapper

# vim:set ft=python sw=4 et spell spelllang=en:
