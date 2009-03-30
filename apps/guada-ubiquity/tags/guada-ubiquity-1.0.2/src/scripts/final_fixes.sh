#!/bin/bash

logs=/target/var/log/installer/debug

exec > $logs 2>&1

function error() {
	echo "Error: $*"
}

cp -v /usr/share/guada-ubiquity/templates/sources.list /target/etc/apt/sources.list || error "copying sources.list"

exit 0
