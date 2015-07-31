# -*- coding: utf-8 -*-

import pytest
from flask_blog.blog import Blog
from flask_blog import app

from flask import url_for


@pytest.fixture()
def two_simple_blogs(tmpdir):
    app.config['FLASK_BLOG_DIR'] = str(tmpdir)
    for (i, which, cat1, cat2) in [
            (1, 'First', 'Category 1', ''),
            (2, 'Second', 'Category 1', '\n    Category 2')]:
        tmpdir.join('blog-{}.md'.format(i)).write(
            '''Title:    {which} blog entry
Summary:  Two line
          summary of my {which} blog entry
Authors:  A.U. Thors
          J. Doe
Categories: {cat1}{cat2}
Slug:     {which}-post
Date:     January 1, 2000
Updated:  January 2, 2000


# {which} blog entry

This is a test paragraph.
'''.format(which=which, cat1=cat1, cat2=cat2))

    tmpdir.join('anotherfile.ext').write('this is ignored')

    blog = Blog()
    blog.init_app(app)
    return blog


def test_markdown_meta_information(two_simple_blogs):
    """ checks that the meta information is read correctly. """
    blog = two_simple_blogs
    blogs = blog.list_blogs()
    assert len(blogs) == 2
    res = blog.get_blog('first-post')
    assert res['title'] == 'First blog entry'


@pytest.mark.xfail
def test_blog_clear_cache_and_reload():
    cache.clear()
    assert not cache.is_filled()
    blogs = list_blogs()
    get_blog(blogs[0])
    old_timestamp = cache.timestamp(blogs[0])
    assert cache.is_filled()

    cache.reload(blogs[0])
    new_timestamp = cache.timestamp(blogs[0])
    assert new_timestamp > old_timestamp


def test_list_blogs(two_simple_blogs):
    blog = two_simple_blogs
    assert len(blog.list_blogs()) == 2
    assert blog.cache.filled
    assert len(blog.list_blogs('category-1')) == 2
    assert len(blog.list_blogs('category-2')) == 1

    blogs = blog.list_blogs()
    assert blogs[0]['title'] == 'First blog entry'
    assert blogs[0]['summary'] == 'Two line\nsummary of my First blog entry'


def test_atom(two_simple_blogs, app, app_ctx):
    target = url_for('blog.recent_feed')
    rv = app.get(target)

    assert 'First blog entry' in rv.data
    assert 'Second blog entry' in rv.data

# vim:set ft=python sw=4 et spell spelllang=en:
