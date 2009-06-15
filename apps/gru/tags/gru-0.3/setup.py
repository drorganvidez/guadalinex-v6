#!/usr/bin/python

from distutils.core import setup
import glob
import os
import re

# look/set what version we have
changelog = "debian/changelog"
if os.path.exists(changelog):
    head=open(changelog).readline()
    match = re.compile(".*\((.*)\).*").match(head)
    if match:
        version = match.group(1)

setup(name='gru',
      version=version,
      packages=[''],
      scripts=['gru'],
      data_files=[
                ('share/applications',['gru.desktop']),
                ('share/pixmaps',['gru.png'])
                ]
)
