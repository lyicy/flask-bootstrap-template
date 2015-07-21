# -*- coding: utf-8 -*-
import os
import jinja2
import subprocess


from . import bookletdir, texsource, read_configuration, list_exercises


def get_renderer():

    # Change the default delimiters used by Jinja such that it won't pick up
    # brackets attached to LaTeX macros.
    loader = jinja2.FileSystemLoader(texsource)
    renderer = jinja2.Environment(
        block_start_string='%{',
        block_end_string='%}',
        variable_start_string='%{{',
        variable_end_string='%}}',
        comment_start_string='%{#',
        comment_end_string='%#}',
        loader=loader,
    )
    return renderer


def _make_tex_file(renderer, conf, template, output):
    template = renderer.get_template(template)
    with open(os.path.join(bookletdir, output), 'w') as fh:
        trender = template.render(**conf)
        fh.write(trender.encode('utf8'))


def render_files():
    renderer = get_renderer()
    conf = read_configuration('conf.yaml', markdown=True, latex=True)
    exercises = list_exercises()
    conf['exercises'] = [os.path.splitext(e)[0] for e in exercises]

    _make_tex_file(renderer, conf, 'booklet.tex', 'flask_blog.tex')

    for exercise in exercises:
        econf = {
            'exercise': read_configuration(
                exercise, markdown=True, latex=True)}
        econf.update(conf)
        output = '{}.tex'.format(os.path.splitext(exercise)[0])
        _make_tex_file(renderer, econf, 'exercise.tex', output)


def run_latexmk():
    try:
        subprocess.check_output(
            ['latexmk', '-pdf', '-f', '-silent', 'flask_blog.tex'],
            cwd=bookletdir)
    except subprocess.CalledProcessError as e:
        print "latexmk returned with error code {}".format(e.returncode)
        print e.output


def make():
    render_files()
    run_latexmk()

# vim:set ft=python sw=4 et spell spelllang=en:
