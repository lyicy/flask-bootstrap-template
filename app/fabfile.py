# -*- coding: utf-8 -*-

import os
from fabric.api import (
    abort, local, task, env, put, run, cd, lcd, prefix)
from contextlib import nested
from datetime import datetime


env.user = 'diviney5'
env.hosts = ['divineproportionpilates.com']


class BluehostConfig(object):

    def __init__(self):
        self.home_dir = '/home6/diviney5'

        self.html_dir = '{}/public_html'.format(self.home_dir)

        self.basedir = os.path.abspath(os.path.dirname(__file__))
        self.git_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..'))
        self.html_dist_dir = '{}/dist'.format(self.git_root)

        self.last_valid_staging = '{}/.last_valid_stage_flask_blog'.format(
            self.home_dir)

        self.backup_root = '{}/flask_blog-backup'.format(self.home_dir)
        run('test -d {dir} || mkdir {dir}'.format(dir=self.backup_root))

        self.db_user = 'diviney5_admin'
        self.db_password = '{]qD8.O2(Z)D~v'

    def _init_paths(self, root_dir):
        self.config_file = '{}/configuration.py'.format(root_dir)
        self.fcgi_file = '{}/flask_flask_blog.fcgi'.format(root_dir)
        self.template_dir = '{}/flask_blog'.format(root_dir)


class StagingConfig(BluehostConfig):

    def __init__(self):
        BluehostConfig.__init__(self)
        self.root_dir = '{}/ptest'.format(self.html_dir)
        self.venv_dir = '{}/ptest/venv'.format(self.html_dir)

        self._init_paths(self.root_dir)
        self.local_config = 'staging.py'

        self.db_backup_prefix = '{}/staging'.format(self.backup_root)
        self.db_name = 'diviney5_flask_blog_test'


class ProductionConfig(BluehostConfig):

    def __init__(self):
        BluehostConfig.__init__(self)
        self.root_dir = '{}/p'.format(self.html_dir)
        self.venv_dir = '{}/venv/flask'.format(self.home_dir)

        self._init_paths(self.root_dir)
        self.local_config = 'production.py'

        self.db_backup_prefix = '{}/production'.format(self.backup_root)
        self.db_name = 'diviney5_flask_blog'


def get_config(deploy_type='production'):
    if deploy_type == 'production':
        return ProductionConfig()
    elif deploy_type == 'staging':
        return StagingConfig()
    else:
        raise ValueError('Unknown deploy_type {}!'.format(deploy_type))


def manage_remote(deploy_type, command):
    cfg = get_config(deploy_type)
    put('manage.py', '{}/manage.py'.format(cfg.root_dir))
    with nested(
        cd(cfg.root_dir),
        prefix('source {}/bin/activate'.format(cfg.venv_dir)),
        prefix('export FLASK_BLOG_SETTINGS={} FLASK_BLOG_ROOT={}'.format(
            cfg.config_file, cfg.template_dir))):

        run('python manage.py {}'.format(command))


@task
def init_db(deploy_type='production'):
    manage_remote(deploy_type, 'init_db')


@task
def db_alembic(deploy_type='production'):
    manage_remote(deploy_type, 'db init')


@task
def db_upgrade(deploy_type='production'):
    manage_remote(deploy_type, 'db upgrade')


@task
def db_migrate(deploy_type='production'):
    manage_remote(deploy_type, 'db migrate')


@task
def backup_db(deploy_type='production'):
    timestamp = datetime.strftime(datetime.now(), '%y%m%d%H%M')
    cfg = get_config(deploy_type)
    backup_file = '{}.{}'.format(cfg.db_backup_prefix, timestamp)
    run(
        ('PGPASSWORD=\'{password}\' pg_dump -U {user} {dbname} '
         '| gzip > {backup_file}')
        .format(
            dbname=cfg.db_name, user=cfg.db_user, password=cfg.db_password,
            backup_file=backup_file))

    with cd(os.path.dirname(backup_file)):
        run(
            'rm -f {prefix}.latest; ln -sf {bf} {prefix}.latest'
            .format(
                bf=os.path.basename(backup_file),
                prefix=cfg.db_backup_prefix))


@task
def restore_db(deploy_type='production', snapshot='latest'):
    cfg = get_config(deploy_type)
    restore_file = '{}.{}'.format(cfg.backup_prefix, snapshot)
    with cd(os.path.dirname(cfg.backup_prefix)):
        run(
            ('gunzip -c {restore_file} '
             '| PGPASSWORD=\'{password}\' psql {dbname} {user}')
            .format(
                restore_file=restore_file,
                dbname=cfg.db_name, user=cfg.db_user,
                password=cfg.db_password))


@task
def pack():
    local('python setup.py sdist --format=gztar', capture=False)


@task
def deploy_html(deploy_type='production'):
    cfg = get_config(deploy_type)
    local('gulp build')
    local_archive = '/tmp/flask_blog_html.tar.gz'
    with lcd(cfg.html_dist_dir):
        local('tar czf {} .'.format(local_archive))

    put(local_archive, '/tmp')
    run('tar xvzf {} -C {}'.format(local_archive, cfg.root_dir))
    local('rm -rf {}'.format(local_archive))
    run('rm -rf {}'.format(local_archive))


@task
def prepare_deploy():
    local('./manage.py test')
    local('git add -p && git commit')
    local('git push')
    pack()


@task
def deploy(deploy_type='production'):
    cfg = get_config(deploy_type)
    tempdir = '/tmp/flask_blog'
    remote_archive = '/tmp/flask_blog.tar.gz'
    dist = local('python setup.py --fullname', capture=True).strip()

    local_archive = 'dist/{}.tar.gz'.format(dist)

    md5sum = local('md5sum {}'.format(local_archive), capture=True).strip()
    if deploy_type == 'production':
        result = run('/bin/bash -c "test \"{}\" == \"$(cat {})\""'.format(
            md5sum, cfg.last_valid_staging))
        if result.failed:
            abort(
                'This archive has not been successfully tested in the staging '
                'phase yet.')

    deploy_html(deploy_type)
    put(local_archive, remote_archive)

    put('{}/configurations/{}'.format(
        cfg.basedir, cfg.local_config),
        cfg.config_file)

    run('mkdir -p {}'.format(tempdir))

    with cd(tempdir):
        run('rm -rf *')
        run('tar -xz --strip-components=1 -f {}'.format(remote_archive))

        with prefix('source {}/bin/activate'.format(cfg.venv_dir)):
            run('python setup.py install')

            run(
                ('FLASK_BLOG_ROOT={flask_blog_root} FLASK_BLOG_SETTINGS={flask_blog_settings} '
                 'python setup.py test')
                .format(
                    flask_blog_root=cfg.template_dir, flask_blog_settings=cfg.config_file))

    run('rm -rf {} {}'.format(tempdir, remote_archive))

    run('''cat <<EOF > {fcgi_file}
#! {venv}/bin/python

import os
from flup.server.fcgi import WSGIServer

os.environ['EA55_ROOT'] = '{root_dir}'
os.environ['EA55_SETTINGS'] = '{flask_blog_settings}'

from flask_blog import app

class ScriptNameStripper(object):
   def __init__(self, app, app_root='/'):
       self.app = app
       self.app_root = app_root

   def __call__(self, environ, start_response):
       environ['SCRIPT_NAME'] = self.app_root.rstrip('/')
       return self.app(environ, start_response)


if __name__ == "__main__":

    if app.config.get('FIX_CGIT', ''):
        app = ScriptNameStripper(app, app_root=app.config['FIX_CGIT'])

    WSGIServer(app).run()

EOF
'''.format(
        venv=cfg.venv_dir, root_dir=cfg.template_dir,
        flask_blog_settings=cfg.config_file, fcgi_file=cfg.fcgi_file))

    run('chmod 755 {}'.format(cfg.fcgi_file))

    if deploy_type == 'staging':
        run('echo {} > {}'.format(md5sum, cfg.last_valid_staging))


# vim:set ft=python sw=4 et spell spelllang=en:
