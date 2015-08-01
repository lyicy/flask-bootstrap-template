# -*- coding: utf-8 -*-

import time
from boto import ec2
from fabric.api import prompt, puts, sudo
from fabric.colors import green
from fabric.state import env

g = {'conn': None}


def get_conn():
    if g['conn'] is None:
        g['conn'] = ec2.connect_to_region(
            env.DEFAULT_REGION,
            aws_access_key=env.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY)
    return g['conn']


def get_instance():
    conn = get_conn()
    reservations = conn.get_all_reservations(
        filters={'tag:Name': env.INSTANCE_NAME})
    if not reservations:
        raise RuntimeError(
            'No instance with name {} found'.format(env.INSTANCE_NAME))
    instance = reservations[0]
    return instance


def init_config():
    conn = get_conn()
    # add ssh security group
    ssh_full = conn.create_security_group('ssh', 'Full SSH access')
    ssh_full.authorize('tcp', 22, 22, '0.0.0.0/0')
    # add web security group
    web = conn.create_security_group('nginx', 'Web server')
    web.authorize('tcp', 80, 80, '0.0.0.0/0')
    web.authorize('tcp', 443, 443, '0.0.0.0/0')


def launch_instance(instance_type='t2.micro'):
    conn = get_conn()
    reservations = conn.get_all_reservations()
    if len(reservations) >= 1:
        res = prompt(
            'You have already one EC2 instance running, are you sure, '
            'that you want to start a new one? (y|N)',
            default='n', validate='[yn]?')
        if res == 'n':
            raise RuntimeError('Instance is already running')

    reservation = conn.run_instances(
        env.BASE_AMI_IMAGE,
        key_name=env.SSH_ID_KEY,
        instance_type=instance_type)

    instance = reservation.instances[0]
    while instance.state != 'running':
        time.sleep(2)
        instance.update()

    puts(green('Instance successfully started') +
         'with IP {ip_address} and dns name {public_dns_name}'
         .format(**instance.__dict__))

    instance.modify_attribute(
        'groupSet',
        [conn.get_all_security_groups(groupnames=['nginx', 'ssh'])])

    addresses = conn.get_all_addresses(addresses=[env.DOMAIN_NAME])
    if len(addresses) == 1:
        address = addresses[0]
    else:
        address = conn.allocate_address(domain=env.DOMAIN_NAME)

    address.associate(instance.id)
    puts(green('Instance is associated with an elastic IP') +
         str(address.public_ip))

    instance.add_tag('Name', env.INSTANCE_NAME)


def prepare_instance():
    sudo('yum update')
    sudo('yum upgrade')
    sudo('yum install nginx')
    sudo('yum service start nginx')
    sudo('pip install --upgrade virtualenv')


def make_root_snapshot(image_name=None):
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
    puts(green('Created a snapshot ') + snapshot)

    if image_name:
        instance.create(image_name[0], image_name[1])

    instance.start()

# vim:set ft=python sw=4 et spell spelllang=en:
