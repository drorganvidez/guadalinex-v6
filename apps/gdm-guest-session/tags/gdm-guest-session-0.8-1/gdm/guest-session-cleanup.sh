#!/bin/sh -e
# (C) 2008 Canonical Ltd.
# Author: Martin Pitt <martin.pitt@ubuntu.com>
# License: GPL v2 or later
#
# Clean up user and temporary home directory for guest session.
# Requires guest account name as $1.

USER="$1"

PWENT=`getent passwd "$USER"` || {
    echo "Error: invalid user $USER"
    exit 1
}
UID=`echo "$PWENT" | cut -f3 -d:`
HOME=`echo "$PWENT" | cut -f6 -d:`

if [ "$UID" -ge 500 ]; then
    echo "Error: user $USER is not a system user."
    exit 1
fi

# kill all remaining processes
while ps h -u "$USER" >/dev/null; do 
    killall -9 -u "$USER" || true
    sleep 0.2; 
done

umount "$HOME" || umount -l "$HOME" || true
rm -rf "$HOME"

# remove leftovers in /tmp
find /tmp -mindepth 1 -maxdepth 1 -uid "$UID" | xargs rm -rf

deluser --system "$USER"

