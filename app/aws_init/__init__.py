# -*- coding: utf-8 -*-

import os
from os.path import join as pjoin, exists as pexists, dirname
import time
from boto import ec2
from fabric.api import prompt, puts, sudo, task, local, require, put, run, env
from fabric.colors import green
from jinja2 import Environment, PackageLoader
from StringIO import StringIO


g = {'conn': None}


def get_conn():
    if g['conn'] is None:
        g['conn'] = ec2.connect_to_region(
            env.DEFAULT_REGION,
            aws_access_key_id=env.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY)
        if g['conn'] is None:
            raise RuntimeError('Could not connect to aws')
    return g['conn']


def get_instance():
    conn = get_conn()
    reservations = conn.get_all_reservations(
        filters={'tag:Name': env.INSTANCE_NAME})
    if not reservations:
        raise RuntimeError(
            'No instance with name {} found'.format(env.INSTANCE_NAME))
    instance = reservations[0].instances[0]
    return instance


@task
def aws_play():
    conn = get_conn()  # noqa
    import pudb
    pudb.set_trace()


@task
def aws_init():
    """
    creates two security groups and uploads the public key

    Security groups
    ===============
    ssh
        grants ssh access everywhere
    nginx
        grants HTTP/HTTPS access from the outside

    Public Key
    ==========

    Specify a public rsa key in your fabfile configuration
    (`env.SSH_KEY_PATH`).
    """

    conn = get_conn()
    # add ssh security group
    existing = [g.name for g in conn.get_all_security_groups()]
    if 'ssh' not in existing:
        ssh_full = conn.create_security_group('ssh', 'Full SSH access')
        ssh_full.authorize('tcp', 22, 22, '0.0.0.0/0')
    if 'nginx' not in existing:
        # add web security group
        web = conn.create_security_group('nginx', 'Web server')
        web.authorize('tcp', 80, 80, '0.0.0.0/0')
        web.authorize('tcp', 443, 443, '0.0.0.0/0')

    existing_keys = conn.get_all_key_pairs(
        filters={'key-name': env.SSH_KEY_ID})
    if env.SSH_KEY_ID not in existing_keys:
        with open(env.SSH_KEY_PATH, 'r') as fh:
            rsa = fh.read()
        conn.import_key_pair(env.SSH_KEY_ID, rsa)


@task
def aws_launch_instance(instance_type='t2.micro'):
    conn = get_conn()
    reservations = conn.get_all_reservations()

    instance = None

    if len(reservations) >= 1:
        try:
            instance = get_instance()
        except RuntimeError:
            res = prompt(
                'You have already one EC2 instance running, are you sure, '
                'that you want to start a new one? (y|N)',
                default='n', validate='[yn]?')
            if res == 'n':
                raise RuntimeError('Instance is already running')

    if not instance:
        reservation = conn.run_instances(
            env.BASE_AMI_IMAGE,
            key_name=env.SSH_KEY_ID,
            instance_type=instance_type)

        instance = reservation.instances[0]
        instance.add_tag('Name', env.INSTANCE_NAME)

    while instance.state != 'running':
        time.sleep(2)
        instance.update()

    puts(green('Instance successfully started') +
         'with IP {ip_address} and dns name {public_dns_name}'
         .format(**instance.__dict__))

    instance.modify_attribute(
        'groupSet',
        conn.get_all_security_groups(['nginx', 'ssh']))

    addresses = conn.get_all_addresses()
    if len(addresses) == 1:
        address = addresses[0]
        res = prompt(
            'You have an elastic IP address {} already. Do you want '
            'to use it for this instance, or create a new one (will cost '
            'money)? (y|N)'.format(address.public_ip),
            default='n', validate='[yn]')
        if res == 'y':
            address = None

    if not address:
        address = conn.allocate_address(domain=env.DOMAIN_NAME)

    if address.public_ip == instance.ip_address:
        puts(
            green('Instance is already associated with elastic IP') +
            str(address.public_ip))
    else:
        address.associate(instance.id)
        puts(green('Instance is associated with an elastic IP') +
             str(address.public_ip))


@task
def aws_prepare_instance():
    sudo('yum update')
    sudo('yum upgrade')
    sudo('yum install nginx git make automake gcc gcc-c++ kernel-devel')
    sudo('service nginx start')
    sudo('pip install --upgrade virtualenv')


@task
def aws_make_root_snapshot(image_slug=None, image_description=None):
    """
    This makes a snapshot of the root volume of your EC2 instance

    If `image_name = ('slug', 'description')` is defined, then an AMI image
    with slug and description is created.
    """
    conn = get_conn()
    instance = get_instance()
    instance.stop()

    volumes = conn.get_all_volumes(
        filters={'attachment.instance-id': instance.id})
    assert len(volumes) == 1
    root_volume = volumes[0]
    root_volume.add_tag('type', 'root')

    snapshot = root_volume.create_snapshot('root-snapshot')
    puts(green('Created a snapshot ') + str(snapshot))

    if image_slug:
        ami = instance.create_image(image_slug, image_description)
        puts(green('Created an ami ') + ami)

    instance.start()


@task
def generate_ssl_key():

    env.ssl_cert_path = pjoin(env.ssl_dir, '{}.crt'.format(env.DOMAIN_NAME))
    env.ssl_key_path = pjoin(env.ssl_dir, '{}.key'.format(env.DOMAIN_NAME))
    if not pexists(env.ssl_dir):
        os.makedirs(env.ssl_dir)

    if not pexists(env.ssl_cert_path):
        # Generate a new private key
        options = dict(
            name=pjoin(env.ssl_dir, env.DOMAIN_NAME),
            length=env.get('length', 2048))

        local(
            'openssl genrsa -passout pass:x -des3 -out {name}.pass.key '
            '{length}'
            .format(**options))
        # strip the password
        local(
            'openssl rsa -passin pass:x -in {name}.pass.key -out {name}.key'
            .format(**options))
        # generate csr
        local(
            'openssl req -nodes -new -key {name}.key -out {name}.csr'
            .format(**options))
        # generate self-signed certificate
        local(
            'openssl x509 -req -days 365 -in {name}.csr -signkey '
            '{name}.key -out {name}.crt'
            .format(**options))

        local(
            'cat {name}.key {name}.crt > {name}.pem'
            .format(**options))


@task
def aws_deploy_nginx_configuration():
    require(
        'DOMAIN_NAME', 'ssl_dir', 'bluegreen_root',
        'nginx_virtual_host_path', 'next_path_abs')
    generate_ssl_key()

    env.remote_ssl_dir = pjoin(env.next_path_abs, 'etc', 'ssl')
    run('mkdir -p {}'.format(env.remote_ssl_dir))
    put(env.ssl_cert_path,
        pjoin(
            env.remote_ssl_dir,
            '{}.crt'.format(env.DOMAIN_NAME)))
    put(env.ssl_key_path,
        pjoin(
            env.remote_ssl_dir,
            '{}.key'.format(env.DOMAIN_NAME)))

    nvhp = env.nginx_virtual_host_path
    DN = env.DOMAIN_NAME
    env.vhost_configuration_path = pjoin(nvhp, '{}.conf'.format(DN))

    res = run(
        'test -f {}'.format(env.vhost_configuration_path),
        quiet=True)

    if res.failed:
        loader = PackageLoader('aws_init')
        jenv = Environment(loader=loader)
        t = jenv.get_template('flask_blog.conf')
        options = {
            'DOMAIN_NAME': env.DOMAIN_NAME,
            'SSL_CERT_PATH': env.ssl_cert_path,
            'SSL_KEY_PATH': env.ssl_key_path,
            'APP_ROOT_DIR': pjoin(env.bluegreen_root)
        }
        conf = StringIO(t.render(**options))
        put(conf, env.vhost_configuration_path, use_sudo=True)

    if 'nginx_options' in env:
        env.fab_configuration_dir = dirname(env.CONFIGURATION_FILE)
        env.nginx_options_path_abs = pjoin(
            env.fab_configuration_dir, env.nginx_options)

        env.remote_nginx_options = pjoin(
            env.next_path_abs, 'etc', 'server_options.conf')
        put(env.nginx_options_path_abs, env.remote_nginx_options)

    sudo('service nginx reload')

# vim:set ft=python sw=4 et spell spelllang=en:
