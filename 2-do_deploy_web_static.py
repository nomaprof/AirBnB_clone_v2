#!/usr/bin/python3
"""Compress web static package using a function
""" 
from os import path
from fabric.api import *
from datetime import datetime


env.hosts = ['100.25.202.252', '35.175.63.185']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'


def do_deploy(archive_path):
        """Deploy the webstatic files to the server
        """
        try:
                if not (path.exists(archive_path)):
                        return False

                # upload the archive to the server
                put(archive_path, '/tmp/')

                # create the path or target directory
                timestamp = archive_path[-18:-4]
                run('sudo mkdir -p /data/web_static/\
releases/web_static_{}/'.format(timestamp))

                # uncompress archive and copy the to new location
                run('sudo tar -xzf /tmp/web_static_{}.tgz -C \
/data/web_static/releases/web_static_{}/'
                    .format(timestamp, timestamp))

                # remove the archive file from /tmp/
                run('sudo rm /tmp/web_static_{}.tgz'.format(timestamp))

                # move contents of webstatic into host web_static
                run('sudo mv /data/web_static/releases/web_static_{}/web_static/* \
/data/web_static/releases/web_static_{}/'.format(timestamp, timestamp))

                # remove the empty webstatic folder caused by uncompressing
                run('sudo rm -rf /data/web_static/releases/\
web_static_{}/web_static'
                    .format(timestamp))

                # delete the already existing symbolic link
                run('sudo rm -rf /data/web_static/current')

                # re-establish the symbolic link again
                run('sudo ln -s /data/web_static/releases/\
web_static_{}/ /data/web_static/current'.format(timestamp))
        except:
                return False

        # return True if execution was successful
        return True
