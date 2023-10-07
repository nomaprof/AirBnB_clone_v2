#!/usr/bin/python3
import os.path
from fabric.api import put
from datetime import datetime
from fabric.api import env
from fabric.api import local
from fabric.api import run

env.hosts = ['100.25.202.252', '35.175.63.185']
env.user = 'ubuntu'
env.key_filename = '~/.ssh/id_rsa'

def do_pack():
    """This function is used to compress the webstatic folder"""
    dt = datetime.utcnow()
    file = "versions/web_static_{}{}{}{}{}{}.tgz".format(dt.year,
                                                         dt.month,
                                                         dt.day,
                                                         dt.hour,
                                                         dt.minute,
                                                         dt.second)
    if os.path.isdir("versions") is False:
        if local("mkdir -p versions").failed is True:
            return None
    if local("tar -cvzf {} web_static".format(file)).failed is True:
        return None
    return file


def do_deploy(archive_path):
    """Send archive to webserver for deployment.

    Args:
        archive_path (str): The path to where the archive can be found
    Returns:
        False, if the archive does not exist in the path
        Otherwise - Return, True
    """
    if os.path.isfile(archive_path) is False:
        return False
    file = archive_path.split("/")[-1]
    name = file.split(".")[0]

    if put(archive_path, "/tmp/{}".format(file)).failed is True:
        return False
    if run("rm -rf /data/web_static/releases/{}/".
           format(name)).failed is True:
        return False
    if run("mkdir -p /data/web_static/releases/{}/".
           format(name)).failed is True:
        return False
    if run("tar -xzf /tmp/{} -C /data/web_static/releases/{}/".
           format(file, name)).failed is True:
        return False
    if run("rm /tmp/{}".format(file)).failed is True:
        return False
    if run("mv /data/web_static/releases/{}/web_static/* "
           "/data/web_static/releases/{}/".format(name, name)).failed is True:
        return False
    if run("rm -rf /data/web_static/releases/{}/web_static".
           format(name)).failed is True:
        return False
    if run("rm -rf /data/web_static/current").failed is True:
        return False
    if run("ln -s /data/web_static/releases/{}/ /data/web_static/current".
           format(name)).failed is True:
        return False
    return True


def gets_out_of_date(number, _type):
    """This function gets the archives that are out of date
    """

    if number == 0:
        number = 1

    if _type == 'local':
        content = local("ls -td web_static_*", capture=True)
    elif _type == 'remote':
        content = run("ls -td web_static_*")

    content_list = content.split()
    out_of_date = content_list[number:]
    return out_of_date


def do_clean(number=0):
    """Remove out-of-date .tgz archives from web servers
    """

    number = int(number)

    if number >= 0:
        with lcd("versions"):
            _files = gets_out_of_date(number, 'local')

            for _file in _files:
                local("rm -f {file}".format(file=_file))

        with cd("/data/web_static/releases"):
            _folders = gets_out_of_date(number, 'remote')

            for _folder in _folders:
                run("rm -rf {folder}".format(folder=_folder))


def deploy():
    """This function helps to create and distribute the archive file to a web server."""
    file = do_pack()
    if file is None:
        return False
    return do_deploy(file)
