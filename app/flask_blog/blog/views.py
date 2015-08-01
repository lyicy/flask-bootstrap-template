# -*- coding: utf-8 -*-
from flask import (
    render_template, Blueprint, jsonify, abort, url_for, request)
from flask.ext.login import login_required
from werkzeug.contrib.atom import AtomFeed

from flask_blog import blog_cache

from ..utils import slugify

blog_blueprint = Blueprint('blog', __name__,)


@blog_blueprint.route('/blog/<category>/<slug>')
def blog(category, slug):
    try:
        blog = blog_cache.get_blog(slug)
        assert category in [slugify(c) for c in blog['categories']]
    except:
        abort(404)

    return render_template(
        'blog.html', category=category, blog=blog, menu={'select': 'blog'})


@blog_blueprint.route('/blog/', defaults={'category': None})
@blog_blueprint.route('/blog/<category>')
def category_listing(category):
    blogs = blog_cache.list_blogs(category=category)
    if category:
        category_name = blog_cache.get_category_name(category)
    else:
        category_name = 'All'

    return render_template(
        'blogs.html',
        category=category,
        category_name=category_name,
        category_blogs=blogs,
        menu={'select': 'blogs'})


@blog_blueprint.route('/api/reload/<slug>')
@login_required
def api_reload_blog(slug=None):
    return jsonify(result='ignored', slug=slug)


@blog_blueprint.route('/api/blog/feed')
def recent_feed():
    """
    Creates an RSS feed.

    Do not forget to put the following in your document

        <link href="{{ url_for('recent_feed') }}"
              rel="alternate"
              title="Recent Changes"
              type="application/atom+xml">
    """
    feed = AtomFeed(
        'Recent Articles',
        feed_url=request.url, url=request.url_root)
    articles = blog_cache.list_blogs()

    for article in articles:
        feed.add(
            article['title'], unicode(article['html']),
            content_type='html',
            author=article['authors'][0],
            url=url_for(
                'blog.blog',
                category=slugify(article['categories'][0]),
                slug=article['slug'],
                _external=True),
            updated=article['updated'],
            published=article['date'])

    return feed.get_response()
# vim:set ft=python sw=4 et spell spelllang=en:
