from distutils.core import setup
import os

#def files():
#	return ['usbcreator/frontend/%s' % n for n in os.listdir('usbcreator/frontend') if n.endswith('.py')]
setup(name='usb-creator',
    version='0.1',
    description='Ubuntu USB desktop image creator',
    author='Evan Dandrea',
    author_email='evand@ubuntu.com',
    packages=['usbcreator'],
    scripts=['bin/usb-creator'],
    #data_files=files(),
    )

