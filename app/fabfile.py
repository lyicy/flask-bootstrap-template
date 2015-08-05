import os
from os.path import join as pjoin, abspath, dirname
from StringIO import StringIO
import yaml

from fabric.api import task, local, run, require, lcd, puts, env, sudo
from fabric.operations import put
from fabric.colors import green

from aws_init import (  # noqa
    aws_init, aws_launch_instance, aws_play, aws_prepare_instance,
    aws_make_root_snapshot, aws_deploy_nginx_configuration,
    aws_deploy_h5bp_nginx_main
)

from gitric.api import (  # noqa
    git_seed, git_reset, allow_dirty, force_push,
    init_bluegreen, swap_bluegreen
)

basedir = abspath(dirname(dirname(__file__)))
env.use_ssh_config = True


def update_env(env, dictionary):
    for key, value in dictionary.iteritems():
        setattr(env, key, value)


@task
def prod(variant='default', env_only=False):

    env.CONFIGURATION_FILE = os.getenv('FABFILE_CONFIGURATION')
    try:
        with open(env.CONFIGURATION_FILE, 'r') as fh:
            config_dict = yaml.load(fh)
    except Exception as e:
        raise ValueError(
            "Environment variable 'FABFILE_CONFIGURATION' needs to point to"
            "a valid configuration file.\n{}".format(e))

    if variant not in config_dict:
        raise ValueError(
            "Specified configuration variant {} not found in configuration")

    update_env(env, config_dict[variant])

    if not env_only:
        init_bluegreen()


@task
def deploy_data(commit=None):
    """
    deploys data, in this case blog entries on the 'next' server
    """
    require('local_data_repo_path')
    with lcd(env.local_data_repo_path):
        env.data_repo_path = pjoin(env.next_path, 'content')
        if not commit:
            commit = local('git rev-parse HEAD', capture=True)
        git_seed(env.data_repo_path, commit)
        git_reset(env.data_repo_path, commit)
    puts(green('Deployed data on the next server'))


@task
def test_unit(dist=False, send_mail=False):
    """
    run unit tests with or without the compiled assets
    """
    if send_mail:
        send_mail = ' --send_mail'
    else:
        send_mail = ''

    environment = ''
    with lcd(pjoin(basedir, 'app')):
        if dist:
            environment = "FLASK_BLOG_ROOT='../../dist/flask_blog' "
            local('gulp build')
        local(
            "FLASK_BLOG_SETTINGS='../configurations/empty.py' {}"
            "py.test --tb short -v tests {}"
            .format(environment, send_mail))


@task
def deploy_templates_assets():
    """
    deploys compiled and minified templates and assets on the 'next' server
    """
    env.html_dist_dir = '../dist/'
    env.html_root_path = pjoin(env.next_path, 'assets')
    local('gulp clean')
    local('gulp build')
    run('mkdir -p {}'.format(env.html_root_path))
    put(env.html_dist_dir, env.html_root_path)
    puts(green('Deployed compiled assets'))


@task
def deploy_app(commit=None):
    if not commit:
        commit = local('git rev-parse HEAD', capture=True)
    env.repo_path = pjoin(env.next_path, 'repo')
    env.relative_assets_path = pjoin(
        '..', '..', '..', 'assets', 'dist', 'flask_blog')
    git_seed(env.repo_path, commit)
    git_reset(env.repo_path, commit)
    run('kill $(cat %(pidfile)s) || true' % env)
    run('virtualenv %(virtualenv_path)s' % env)
    run('source %(virtualenv_path)s/bin/activate && '
        'pip install -r %(repo_path)s/app/requirements.txt'
        % env)
    put(StringIO('proxy_pass http://127.0.0.1:%(bluegreen_port)s/;' % env),
        env.nginx_conf)
    put(env.app_configuration, pjoin(env.next_path, 'configuration.py'))
    run('cd %(repo_path)s/app && PYTHONPATH=. '
        'BLUEGREEN="%(color)s" '
        'FLASK_BLOG_SETTINGS="../../../configuration.py" '
        'FLASK_BLOG_ROOT="%(relative_assets_path)s" '
        '%(virtualenv_path)s/bin/gunicorn --preload -D '
        '--log-file %(next_path)s/gunicorn.log '
        '-b 0.0.0.0:%(bluegreen_port)s -p %(pidfile)s flask_blog:app '
        '&& sleep 1'
        % env)


@task
def suspend_next_task():
    """
    suspend the next.(DOMAIN_NAME) server in order to save resources
    """
    require('pidfile')
    run('kill $(cat %(pidfile)s) || true' % env)
    puts(green(
        'Suspended the next.%(DOMAIN_NAME)s server.  Run deploy_app task to '
        're-start.' % env))


@task
def reload_web_server():
    sudo('service nginx reload')


@task
def deploy_all(app_commit=None, data_commit=None):
    deploy_data(data_commit)
    deploy_templates_assets()
    deploy_app(app_commit)


@task
def cutover():
    swap_bluegreen()
    reload_web_server()

# vim:set ft=python sw=4 et spell spelllang=en:
