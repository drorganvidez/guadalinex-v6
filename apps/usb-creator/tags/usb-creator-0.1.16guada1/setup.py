from distutils.core import setup
from DistUtilsExtra.command import *
import os

setup(name='usb-creator',
    version='0.1.12',
    description='Ubuntu USB desktop image creator',
    author='Evan Dandrea',
    author_email='evand@ubuntu.com',
    packages=['usbcreator'],
    scripts=['bin/usb-creator'],
    data_files=[],
    cmdclass = { "build" : build_extra.build_extra,
        "build_i18n" :  build_i18n.build_i18n,
        "build_help" :  build_help.build_help,
        "build_icons" :  build_icons.build_icons,
        "clean": clean_i18n.clean_i18n, 
        }
    )

