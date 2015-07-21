# -*- coding: utf-8 -*-

from flask_blog.exercises import list_exercises


def test_list_exercises():
    assert len(list_exercises()) == 2

# vim:set ft=python sw=4 et spell spelllang=en:
