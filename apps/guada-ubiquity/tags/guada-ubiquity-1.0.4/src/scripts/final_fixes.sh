#!/bin/bash

logs=/target/var/log/installer/debug

exec >> $logs 2>&1

function error() {
	echo "Error: $*"
}

# set custom guadalinex sources.list
cp -v /usr/share/guada-ubiquity/templates/sources.list /target/etc/apt/sources.list || error "copying sources.list"

# force openssh-server to regenerate keys
for file in ssh_host_dsa_key ssh_host_dsa_key.pub ssh_host_rsa_key ssh_host_rsa_key.pub
do
	test -f /target/etc/ssh/$file && rm -f /target/etc/ssh/$file
done
chroot /target dpkg-reconfigure openssh-server

exit 0
