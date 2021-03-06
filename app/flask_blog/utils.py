# -*- coding: utf-8 -*-
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect, abort, g, current_app
import re
import translitcodec  # noqa
from datetime import datetime

_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def datetime_filter(s, form='medium'):
    if not s:
        return
    if form == 'full':
        format = "%B %d, %Y 'at' %H:%M"
    elif form == 'medium':
        format = "%B %d, %Y"
    return datetime.strftime(s, format)


def canonical_filter(s):
    res = urljoin(
        current_app.config.get(
            'CANONICAL_SERVER', request.url_root),
        url_for(request.url_rule.endpoint,
                **request.view_args))
    return res


def after_app_teardown(f):
    callbacks = getattr(g, 'on_teardown_callbacks', None)
    if callbacks is None:
        g.on_teardown_callbacks = callbacks = []
    callbacks.append(f)
    return f


def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = word.encode('translit/long')
        if word:
            result.append(word)
    return unicode(delim.join(result))


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return (
        test_url.scheme in ('http', 'https') and
        ref_url.netloc == test_url.netloc)


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form.get('next')
    if not target:
        target = url_for(endpoint, **values)
    elif not is_safe_url(target):
        abort(400)
    return redirect(target)

# vim:set ft=python sw=4 et spell spelllang=en:
