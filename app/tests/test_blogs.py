# -*- coding: utf-8 -*-

import pytest
from flask_blog.blog import list_blogs, cache, get_blog


@pytest.fixture()
def two_simple_blogs(tempdir):
    pass


def test_markdown_meta_information():
    """ checks that the meta information is read correctly. """
    blogs = list_blogs()
    get_blog(blogs[0])


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
    assert len(list_blogs()) == 2
    assert cache.is_filled()
    assert len(list_blogs('Category 1')) == 2
    assert len(list_blogs('Category 2')) == 1

    blogs = list_blogs(slug=False, title=True, summary=True)
    assert blogs[0]['title'] == 'First blog entry'
    assert blogs[0]['summary'] == 'Summary of first blog entry'

# vim:set ft=python sw=4 et spell spelllang=en:
