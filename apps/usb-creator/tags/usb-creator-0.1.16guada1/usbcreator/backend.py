# Copyright (C) 2008  Canonical, Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import subprocess, sys
import stat
import shutil
import gobject
import dbus
from dbus.mainloop.glib import DBusGMainLoop

def popen(cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    res = process.communicate()
    return process, res

def free_space(dev):
    stat = os.statvfs(dev)
    return stat.f_bsize * stat.f_bavail

class Backend:
    def __init__(self, frontend):
        self.source_devices = {}
        self.devices = {}
        self.frontend = frontend
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.Bus(dbus.Bus.TYPE_SYSTEM)
        hal_obj = self.bus.get_object('org.freedesktop.Hal',
            '/org/freedesktop/Hal/Manager')
        self.hal = dbus.Interface(hal_obj, 'org.freedesktop.Hal.Manager')

    def set_install_source(self, source):
        # TODO: Make more consistent with install_target
        self.install_source = source

    def set_install_target(self, target):
        self.install_target = self.devices[target]
    
    def device_added(self, udi):
        dev_obj = self.bus.get_object("org.freedesktop.Hal", udi)
        dev = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        success = False
        # Look for the volume first as it may not have appeared yet when you
        # check the parent.
        if dev.PropertyExists('block.is_volume') and dev.GetProperty('block.is_volume'):
            if (dev.PropertyExists('storage.bus') and
                dev.GetProperty('storage.bus') == 'usb') and \
                dev.GetProperty('storage.removable'):
                success = True
            else:
                p = dev.GetProperty('info.parent')
                dev_obj = self.bus.get_object('org.freedesktop.Hal', p)
                d = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
                if (d.PropertyExists('storage.bus') and # necessary?
                    d.GetProperty('storage.bus') == 'usb') and \
                    d.GetProperty('storage.removable'):
                    success = True
            if success:
                self.add_device(dev)
                dev.connect_to_signal(signal_name="PropertyModified", handler_function=self.property_modified)

    def property_modified(self, num_changes, changes):
        # FIXME: useless until we can pass in the udi of the device that's
        # being changed.
        print 'property modified:'
        for c in changes:
            print 'change: %s' % str(c[0])

    def device_removed(self, udi):
        d = None
        for device in self.devices.itervalues():
            if device['udi'] == udi:
                print 'removing %s' % udi
                d = device['device']
        if d:
            self.devices.pop(d)
            # TODO: Move into the frontend in a generic function.
            to_delete = None
            m = self.frontend.dest_combo.get_model()
            iterator = m.get_iter_first()
            while iterator is not None:
                if m.get_value(iterator, 0) == d:
                    to_delete = iterator
                iterator = m.iter_next(iterator)
            if to_delete is not None:
                m.remove(to_delete)
    def add_device(self, dev):
        mountpoint = str(dev.GetProperty('volume.mount_point'))
        device = str(dev.GetProperty('block.device'))
        self.devices[device] = {
            'label' : str(dev.GetProperty('volume.label')).replace(' ', '_'),
            'fstype' : str(dev.GetProperty('volume.fstype')),
            'uuid' : str(dev.GetProperty('volume.uuid')),
            'mountpoint' : mountpoint,
            'udi' : str(dev.GetProperty('info.udi')),
            'free' : mountpoint and free_space(mountpoint) or 0,
            'device' : device
        }
        print 'new device:\n%s' % self.devices[device]
        self.frontend.add_dest(device)
    
    def detect_devices(self):
        # TODO: Handle devices with empty partition tables.
        devices = self.hal.FindDeviceByCapability('storage')
        for device in devices:
            dev_obj = self.bus.get_object('org.freedesktop.Hal', device)
            d = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
            if d.GetProperty('storage.bus') == 'usb' and \
                d.GetProperty('storage.removable'):
                if d.GetProperty('block.is_volume'):    
                    self.add_device(d)
                else:
                    children = self.hal.FindDeviceStringMatch('info.parent', device)
                    for child in children:
                        dev_obj = self.bus.get_object('org.freedesktop.Hal', child)
                        child = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
                        if child.GetProperty('block.is_volume'):
                            self.add_device(child)
                            # TODO: should we break here?

        self.bus.add_signal_receiver(self.device_added,
            "DeviceAdded",
            "org.freedesktop.Hal.Manager",
            "org.freedesktop.Hal",
            "/org/freedesktop/Hal/Manager")
        self.bus.add_signal_receiver(self.device_removed,
            "DeviceRemoved",
            "org.freedesktop.Hal.Manager",
            "org.freedesktop.Hal",
            "/org/freedesktop/Hal/Manager")

    def mount_iso(self, filename):
        # TODO: This should be automatically picked up by a modified
        # device_added function that handles source devices in the form of
        # CD-ROMs and mounted ISO files.  It should probably call out to a
        # separate function for this to ease readability.
        # Actually, HAL doesn't seem to support loop mounted filesystems and
        # indeed when manually mounted, the device does not appear in d-feet
        # (searching the mountpoint).  We'll probably have to just manually
        # construct the addition to self.devices, which probably makes a fair
        # amount of sense anyway.
        import tempfile
        print 'mounting %s' % filename
        tmpdir = tempfile.mkdtemp()
        res = popen('mount -o loop,ro %s %s' % (filename, tmpdir))
        if res[0].returncode:
            print 'unable to mount %s to %s' % (filename, tmpdir)
            print res[1]
        fp = None
        try:
            fp = open('%s/.disk/info' % tmpdir)
            line = fp.readline()
            line = ' '.join(line.split(' ')[:2])
            size = os.stat(filename).st_size
            self.source_devices[filename] = { 'title' : line,
                                              'filename' : filename,
                                              'size' : size }
            self.frontend.add_source(filename)
        except Exception, e:
            print 'Unable to find %s/.disk/info, not using %s' % \
                (tmpdir, filename)
            print str(e)
            fp.close()
            popen('umount %s' % tmpdir)
            popen('rmdir %s' % tmpdir)

        fp.close()
        popen('umount %s' % tmpdir)
        popen('rmdir %s' % tmpdir)

    def install_bootloader(self):
        # TODO: Needs to be moved into the generic install routine.
        # TODO: mark install_target['device'] as bootable using sfdisk or similar.
        print 'installing the bootloader to %s.' % self.install_target['device']
        process = popen('syslinux -s %s' % self.install_target['device'])[0]
        if process.returncode:
            print 'Error installing the bootloader (syslinux -s %s)' % self.install_target['device']

    def copy_files(self):
        # TODO: md5 on copy as well?
        tmpdir = ''
        def _copy_files():
            # TODO: debate pulling the total_size bit in from ubiquity for more
            # accurate progress.
            # TODO: Fedora's program shells out to cp and uses another thread that
            # checks the free space on the drive and updates the UI accordingly.
            # Is this worth replicating?
            #cmd = '/home/evan/usb-creator/install.py -s %s -t %s' % (tmpdir, self.install_target['mountpoint'])
            cmd = 'cp -ra %s/. %s' % (tmpdir, self.install_target['mountpoint'])
            cmd = cmd.split(' ')
            print cmd
            self.pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            #gobject.io_add_watch(self.pipe.stdout,
            #         gobject.IO_IN | gobject.IO_HUP,
            #         self.data_available)
            #gobject.io_add_watch(self.pipe.stderr,
            #         gobject.IO_IN | gobject.IO_HUP,
            #         self.data_available)
            # Wait for the process to complete
            gobject.child_watch_add(self.pipe.pid, self.on_end)

        import tempfile
        print 'mounting'
        if self.install_source.lower().endswith('.iso'):
            tmpdir = tempfile.mkdtemp()
            popen('mount -o loop,ro %s %s' % (self.install_source, tmpdir))
            try:
                print 'copying from ISO...'
                _copy_files()
            finally:
                popen('umount %s' % tmpdir)
                popen('rmdir %s' % tmpdir)
        else:
            tmpdir = tempfile.mkdtemp()
            popen('mount -o ro %s %s' % (self.install_source, tmpdir))
            try:
                print 'copying from CD...'
                _copy_files()
            finally:
                popen('umount %s' % tmpdir)
    def on_end(self, pid, error_code):
        # FIXME: move into install.py
        popen('rm -rf %s/syslinux' % self.install_target['mountpoint'])
        popen('mv %s/isolinux %s/syslinux' %
            (self.install_target['mountpoint'], self.install_target['mountpoint']))
        popen('mv %s/syslinux/isolinux.cfg %s/syslinux/syslinux.cfg' %
            (self.install_target['mountpoint'], self.install_target['mountpoint']))
        print 'error_code %d' % error_code
        print 'All done.'
        self.frontend.quit()
    def data_available(self, source, condition):
        #print 'data_available'
        #return False
        data = ''
        while True:
            try:
                #c=self.pipe.read(1)
                c = source.read(1)
            except ValueError:
                break
            data+=c
            #print 'Read',data
            if c=='\n':
                break
        if data:
            print 'data: %s' % data
            self.frontend.progress(int(data.strip('\n')))
            return True
        else:
            return False
        #text = source.readline()
        #if len(text) > 0:
        #    #print 'data: %s' % text.strip('\n')
        #    self.frontend.progress(int(text.strip('\n')))
        #    return True
        #else:
        #    return False

    def create_persistence_file(self):
        # FIXME: Needs to get the count size from the frontend.  Also needs to tell
        # the frontend the max size for the count.  The minimum should be static,
        # something like 128 MB.
        # FIXME: move into install.py
        popen('dd if=/dev/zero of=%s/casper-rw bs=1M count=128' % self.install_target['mountpoint'])
        popen('mkfs.ext3 -F %s/casper-rw' % self.install_target['mountpoint'])
        # add persistence option to syslinux.cfg
