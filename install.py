#!/usr/bin/env python

# This script will use the correct repo to install packages for clusterhq-flocker-node

import sys

# Usage: deploy.py cluster.yml
from utils import Configurator

if __name__ == "__main__":
    c = Configurator(configFile=sys.argv[1])
    for node in c.config["agent_nodes"]:
        if c.config["os"] == "ubuntu":
            c.runSSH(node, """apt-get -y install apt-transport-https software-properties-common
add-apt-repository -y ppa:james-page/docker
add-apt-repository -y 'deb https://clusterhq-archive.s3.amazonaws.com/ubuntu-testing/14.04/$(ARCH) /'
apt-get update
apt-get -y --force-yes install clusterhq-flocker-node
""")
        elif c.config["os"] == "centos":
            c.runSSH(node, """if selinuxenabled; then setenforce 0; fi
test -e /etc/selinux/config && sed --in-place='.preflocker' 's/^SELINUX=.*$/SELINUX=disabled/g' /etc/selinux/config
yum install -y https://s3.amazonaws.com/clusterhq-archive/centos/clusterhq-release$(rpm -E %dist).noarch.rpm
yum install -y clusterhq-flocker-node
""")

    if c.config["agent_config"]["dataset"]["backend"] == "zfs":
        if c.config["os"] == "centos":
            print "Auto-install of ZFS on centos not currently supported - restart required"

        for node in c.config["agent_nodes"]:
            if c.config["os"] == "ubuntu":
                c.runSSH(node, """add-apt-repository -y ppa:zfs-native/stable
apt-get update
apt-get -y install libc6-dev
apt-get -y install zfsutils
mkdir -p /var/opt/flocker
truncate --size 10G /var/opt/flocker/pool-vdev
zpool create flocker /var/opt/flocker/pool-vdev
""")

    print "Installed clusterhq-flocker-node on all nodes"
    print "To configure and deploy the cluster:"
    print "./deploy.py cluster.yml"
