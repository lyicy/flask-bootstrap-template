# -*- coding: utf-8 -*-
import mistune
import os
import yaml

from ..latex_renderer import markdown_latex


basedir = os.path.dirname(__file__)
bookletdir = os.path.abspath(os.path.join(
    basedir, '../../booklet'))
texsource = os.path.abspath(os.path.join(
    basedir, '../../booklet/_source'))
confsource = os.path.abspath(os.path.join(
    basedir, '../templates/exercises'))


def get_title(filename):
    conf = read_configuration(filename)
    return conf['title']


def read_configuration(filename, markdown=False, latex=False):
    with open(os.path.join(confsource, filename), 'r') as fh:
        conf = yaml.load(fh)
    if markdown:
        conf = md2html(conf, latex=latex)
    return conf


def list_exercises():
    l = os.listdir(confsource)
    l = [e for e in l
         if (e.endswith('.yaml') and not e.endswith('_old.yaml'))]
    l.remove('conf.yaml')
    return l


def md2html(conf, latex=False):
    nconf = {}
    skip_keys = ['title_picture', 'title', 'video']
    for key, value in conf.iteritems():
        if key in skip_keys:
            nconf[key] = value
        elif type(value) == dict:
            nconf[key] = md2html(value, latex)
        elif isinstance(value, basestring):
            if latex:
                nconf[key] = markdown_latex(value)
            else:
                nconf[key] = mistune.markdown(value)
    return nconf

# vim:set ft=python sw=4 et spell spelllang=en:
