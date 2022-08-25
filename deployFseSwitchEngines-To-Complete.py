import errno
import os
import subprocess
import openstack
from openstack import connection
from openstack import utils
from getpass import getpass
from base64 import b64encode


def get_credentials(provider, filename):
    """
        The config file should have the follwing format
        [switch]
        project = <your_project_name>
        username = <your_username>
        region = <region>
        keypair = <your_keypair>
        secgrp  = <your_secgrp>
        [aws]
        keypair = <your_keypair>
        secgrp  = <your_secgrp>
        """

    import configparser
    from getpass import getpass
    cp = configparser.ConfigParser()
    cp.read(filename)
    provider = 'switch'
    return (cp.get(provider, 'project') + ':' + cp.get(provider, 'username'), getpass(), cp.get(provider, 'region'),
            cp.get(provider, 'keypair'), cp.get(provider, 'secgrp'))


def create_connection(auth_url, access, password, region):
    ''' to Compltete ...'''


def delete_server(conn, srv):
    ''' to Compltete ...'''


def create_server(conn, name, img, flv, net, key, grp, userdata=""):
    ''' to Compltete ...'''


def get_unused_floating_ip(conn, public_network='public'):
    ''' to Compltete ...'''


def attach_floating_ip_to_instance(conn, instance, floating_ip):
    ''' to Compltete ...'''


def main():
    AUTH_URL = "https://keystone.cloud.switch.ch:5000/v3"
    network = 'private'

    SPOTIFY_ID = "..."
    SPOTIFY_SECRET = "..."
    EVENTFUL = "..."
    GMAP = "..."

    MONGO_IMG = 'mongodb_img'
    BACKEND_IMG = 'backend_img'
    FRONTEND_IMG = 'frontend_img'

    print("Login phase...")
    access, secret, region, keypair, secgrp = get_credentials('switch', 'provider.conf')
    conn = create_connection(AUTH_URL, access, secret, region)

    print("Creating MongoDB instance: ")
    mongo = create_server(conn, "mongodb", MONGO_IMG, 'm1.small', network, keypair, secgrp)

    mongo = conn.get_server_by_id(mongo.id)  # refresh instance data
    MONGO_IP = mongo.private_v4
    DATABASE = "mongodb://%s:%d/festivaldb" % (MONGO_IP, 27017)

    print("Creating BackEnd instance: ")
    userdata = '''#!/usr/bin/env bash
cd /home/ubuntu/FSEArchive/server
echo "SPOTIFY_ID=%s" > /home/ubuntu/FSEArchive/server/keys.env
echo "SPOTIFY_SECRET=%s" >> /home/ubuntu/FSEArchive/server/keys.env
echo "EVENTFUL=%s" >> /home/ubuntu/FSEArchive/server/keys.env
echo "DATABASE=%s" >> /home/ubuntu/FSEArchive/server/keys.env
nohup /home/ubuntu/FSEArchive/node-v8.11.4-linux-x64/bin/node start.js > /dev/null &
''' % (SPOTIFY_ID, SPOTIFY_SECRET, EVENTFUL, DATABASE)
    api = create_server(conn, 'backend', BACKEND_IMG, 'm1.small', network, keypair, secgrp, userdata)
    floating_ip = get_unused_floating_ip(conn)
    print("Backend IP:", floating_ip.floating_ip_address)
    attach_floating_ip_to_instance(conn, api, floating_ip)
    api = conn.get_server_by_id(api.id)  # refresh instance data

    print("Creating FrontEnd instance: ")
    userdata = '''#!/usr/bin/env bash
cd /home/ubuntu/FSEArchive/client
echo "GMAP=%s" >> /home/ubuntu/FSEArchive/client/keys.env
nohup /home/ubuntu/FSEArchive/node-v8.11.4-linux-x64/bin/node start.js --serverPublic=%s > /dev/null &
''' % (GMAP, "http://" + api.public_v4 + ":3000")
    front = create_server(conn, 'frontend', FRONTEND_IMG, 'm1.small', network, keypair, secgrp, userdata)
    floating_ip = get_unused_floating_ip(conn)
    print("Frontend IP:", floating_ip.floating_ip_address)
    attach_floating_ip_to_instance(conn, front, floating_ip)

    delete = 'N'

    while delete != 'A':
        delete = input('Abort (A) ?')

    delete_server(conn, mongo)
    delete_server(conn, api)
    delete_server(conn, front)


if __name__ == "__main__":
    main()
