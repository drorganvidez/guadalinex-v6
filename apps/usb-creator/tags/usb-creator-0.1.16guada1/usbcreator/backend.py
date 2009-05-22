# Copyright (C) 2008 Canonical Ltd.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
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
import time
import tempfile

class Logger:
    def __init__ (self):
        if 'SUDO_USER' in os.environ:
            log_file = '%s/.usb-creator.log' % \
                os.path.expanduser('~' + os.environ['SUDO_USER'])
        else:
            log_file = '%s/.usb-creator.log' % \
                os.path.expanduser('~')
        self.fp = open(log_file, 'a')
        self.save = sys.stderr
        sys.stderr = self
        self.new_line = 1
        l = '\n-- Starting up at %s --\n' % time.strftime('%H:%M:%S')
        self.fp.write(l)
        self.fp.flush()
        sys.stdout.write(l)
        sys.stdout.flush()

    def __del__(self):
        self.fp.close()
        self.stderr = self.save

    def fileno(self):
        return self.fp.fileno()

    def write(self, line):
        if (self.new_line):
            l = '[%s] ' % time.strftime('%H:%M:%S')
            self.new_line = 0
            l = l + line
        else:
            l = line

        self.fp.write(l)
        self.fp.flush()
        sys.stdout.write(l)
        sys.stdout.flush()
        if (line[-1] == '\n'):
            self.new_line = 1

def popen(cmd):
    print >>sys.stderr, str(cmd)
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
        stderr=sys.stderr, stdin=subprocess.PIPE)
    res = process.communicate()
    return process, res

def free_space(dev):
    try:
        stat = os.statvfs(dev)
    except:
        # This could get called in the event loop as we're shutting down, after
        # we've unmounted filesystems.
        return 0
    return stat.f_bsize * stat.f_bavail

class Backend:
    def __init__(self, frontend):
        self.devices = {}
        self.cds = {}
        self.timeouts = {}
        self.copy_timeout = 0
        self.original_size = 0
        self.progress_description = ''
        self.frontend = frontend
        self.logger = Logger()
        DBusGMainLoop(set_as_default=True)
        self.bus = dbus.Bus(dbus.Bus.TYPE_SYSTEM)
        hal_obj = self.bus.get_object('org.freedesktop.Hal',
            '/org/freedesktop/Hal/Manager')
        self.hal = dbus.Interface(hal_obj, 'org.freedesktop.Hal.Manager')
        self.pipe = None

    def log(self, line):
        # It might make more sense to just reassign stdout since we're logging
        # everything anyway.
        line = str(line) + '\n'
        self.logger.write(line)

    def set_install_source(self, source):
        # TODO: Make more consistent with install_target
        self.install_source = source

    def set_install_target(self, target):
        self.install_target = self.devices[target]

    def set_persistence_size(self, persist):
        self.persistence_size = persist

    def format_device(self, device):
        udi = self.hal.FindDeviceStringMatch('block.device', device)
        udi = udi[0]
        children = self.hal.FindDeviceStringMatch('info.parent', udi)
        for child in children:
            dev_obj = self.bus.get_object('org.freedesktop.Hal', child)
            child = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
            dev = str(child.GetProperty('block.device'))
            popen(['umount', dev])
        popen(['umount', device])

        # TODO: This could really use a progress dialog.
        res = popen(['parted', '-s', device, 'mklabel', 'msdos'])
        if res[0].returncode:
            message = _('Unable to create a partition table:') + '\n' + str(res[1][0])
            self.log(message)
            self.frontend.notify(message)
            return
        res = popen(['parted', '-s', device, 'mkpartfs', 'primary', 'fat32', '0', '--', '-0'])
        if res[0].returncode:
            message = _('Unable to format device:') + '\n' + str(res[1][0])
            self.log(message)
            self.frontend.notify(message)
        else:
            self.devices.pop(device)
            self.frontend.device_removed(device, source=False)
    
    def device_added(self, udi):
        self.log('possibly adding: ' + str(udi))
        dev_obj = self.bus.get_object("org.freedesktop.Hal", udi)
        dev = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        if dev.PropertyExists('volume.is_disc') and dev.GetProperty('volume.is_disc'):
            if not dev.GetProperty('volume.disc.is_blank'):
                self.log('got a disc: %s' % dev.GetProperty('volume.label'))
                self.bus.add_signal_receiver(self.property_modified,
                'PropertyModified', 'org.freedesktop.Hal.Device',
                'org.freedesktop.Hal', udi, path_keyword='udi')
        # Look for the volume first as it may not have appeared yet when you
        # check the parent.
        success = False
        if dev.PropertyExists('block.is_volume') and dev.GetProperty('block.is_volume'):
            if (dev.PropertyExists('storage.bus') and
            dev.GetProperty('storage.bus') == 'usb') and \
            dev.GetProperty('storage.removable'):
                if dev.GetProperty('volume.fstype') == 'vfat':
                    success = True
                else:
                    self.log('didnt add because not vfat')
            else:
                p = dev.GetProperty('info.parent')
                dev_obj = self.bus.get_object('org.freedesktop.Hal', p)
                d = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
                if (d.PropertyExists('storage.bus') and
                d.GetProperty('storage.bus') == 'usb') and \
                d.GetProperty('storage.removable'):
                    if dev.GetProperty('volume.fstype') == 'vfat':
                        success = True
            if success:
                self.add_device(dev)
                return
        # Look for empty devices.
        if self.IsStorageDevice(dev):
            children = self.hal.FindDeviceStringMatch('info.parent', udi)
            c = False
            for child in children:
                dev_obj = self.bus.get_object('org.freedesktop.Hal', child)
                child = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
                if child.GetProperty('block.is_volume') and child.GetProperty('volume.fstype') == 'vfat':
                    c = True
                self.log('children: ' + str(children))
            if not c and dev.PropertyExists('storage.removable.media_size'):
                self.log('no children or children not vfat')
                device = str(dev.GetProperty('block.device'))
                self.devices[device] = {
                    'label' : '',
                    'fstype' : '',
                    'uuid' : '',
                    'mountpoint' : '',
                    'udi' : udi,
                    'free' : dev.GetProperty('storage.removable.media_size'),
                    'capacity' : dev.GetProperty('storage.removable.media_size'),
                    'device' : device
                }
                self.frontend.add_dest(device)

    def property_modified(self, num_changes, change_list, udi):
        dev_obj = self.bus.get_object("org.freedesktop.Hal", udi)
        dev = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        if dev.PropertyExists('volume.is_disc') and dev.GetProperty('volume.is_disc'):
            if not dev.GetProperty('volume.is_mounted'):
                return
            mountpoint = dev.GetProperty('volume.mount_point')
            # TODO: Is the most appropriate check?
            if mountpoint and os.path.exists('%s/.disk/info' % mountpoint):
                add = False
                if not self.cds.has_key(udi):
                    add = True
                self.cds[udi] = {
                    'label' : str(dev.GetProperty('volume.label')),
                    'uuid' : str(dev.GetProperty('volume.uuid')),
                    'mountpoint' : mountpoint,
                    'udi' : udi,
                    'size' : dev.GetProperty('volume.size'),
                    'filename' : '',
                }
                if add:
                    self.frontend.add_source(udi)
                self.frontend.update_all_rows(None)
        else:
            mountpoint = str(dev.GetProperty('volume.mount_point'))
            device = str(dev.GetProperty('block.device'))
            self.devices[device] = {
                'label' : str(dev.GetProperty('volume.label')).replace(' ', '_'),
                'fstype' : str(dev.GetProperty('volume.fstype')),
                'uuid' : str(dev.GetProperty('volume.uuid')),
                'mountpoint' : mountpoint,
                'udi' : str(dev.GetProperty('info.udi')),
                'free' : mountpoint and free_space(mountpoint) or 0,
                'capacity' : dev.GetProperty('volume.size'),
                'device' : device
            }
            self.frontend.update_dest_row(device)
        self.log('prop modified')
        self.log('device_udi: %s' % udi)
        self.log('num_changes: %d' % num_changes)
        for c in change_list:
            self.log('change: %s' % str(c[0]))

    def device_removed(self, udi):
        d = None
        for device in self.devices.itervalues():
            if device['udi'] == udi:
                self.log('removing %s' % udi)
                d = device['device']
                break
        if d:
            self.devices.pop(d)
            self.frontend.device_removed(d, source=False)
            gobject.source_remove(self.timeouts[d])
            self.timeouts.pop(d)
        else:
            # TODO: Ick.
            d = None
            for device in self.cds.itervalues():
                if device['udi'] == udi:
                    self.log('removing %s' % udi)
                    d = udi
                    break
            if d:
                self.cds.pop(d)
                self.frontend.device_removed(d, source=True)
            
    def add_device(self, dev):
        # Remove parent device if present as this means there is not an empty
        # partition table.
        dev_obj = self.bus.get_object("org.freedesktop.Hal",
            dev.GetProperty('info.parent'))
        device = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        d = device.GetProperty('block.device')
        if self.devices.has_key(d):
            self.devices.pop(d)
            self.frontend.device_removed(d, source=False)

        udi = dev.GetProperty('info.udi')
        mountpoint = str(dev.GetProperty('volume.mount_point'))
        device = str(dev.GetProperty('block.device'))
        self.devices[device] = {
            'label' : str(dev.GetProperty('volume.label')).replace(' ', '_'),
            'fstype' : str(dev.GetProperty('volume.fstype')),
            'uuid' : str(dev.GetProperty('volume.uuid')),
            'mountpoint' : mountpoint,
            'udi' : str(dev.GetProperty('info.udi')),
            'free' : mountpoint and free_space(mountpoint) or 0,
            'capacity' : dev.GetProperty('volume.size'),
            'device' : device
        }
        self.bus.add_signal_receiver(self.property_modified,
        'PropertyModified', 'org.freedesktop.Hal.Device',
        'org.freedesktop.Hal', udi, path_keyword='udi')
        self.log('new device:\n%s' % self.devices[device])
        self.frontend.add_dest(device)
        def update_free(device):
            dev = self.devices[device]
            mp = dev['mountpoint']
            free = dev['free']
            if mp:
                dev['free'] = free_space(mp)
                if free != dev['free']:
                    self.frontend.update_dest_row(device)
            else:
                # TODO: Is here really the best place for this?
                fstype = dev['fstype']
                if not fstype:
                    return True
                dev_obj = self.bus.get_object("org.freedesktop.Hal", str(dev['udi']))
                d = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
                if d.GetProperty('volume.mount_point'):
                    return True
                tmpdir = tempfile.mkdtemp()
                res = popen(['mount', '-t', fstype, device, tmpdir])
                if res[0].returncode:
                    self.log('Error mounting %s: %s' % (device, res[1]))
                    popen(['rmdir', tmpdir])
                else:
                    dev['mountpoint'] = tmpdir
            return True
        self.timeouts[device] = gobject.timeout_add(2000, update_free, device)
    
    def detect_devices(self):
        # TODO: Handle devices with empty partition tables.
        # CDs
        devices = self.hal.FindDeviceByCapability('volume')
        for device in devices:
            dev_obj = self.bus.get_object('org.freedesktop.Hal', device)
            dev = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
            if dev.PropertyExists('volume.is_disc') and dev.GetProperty('volume.is_disc'):
                if not dev.GetProperty('volume.disc.is_blank'):
                    self.log('got a disc: %s' % dev.GetProperty('volume.label'))
                    udi = dev.GetProperty('info.udi')
                    if not dev.GetProperty('volume.is_mounted'):
                        self.bus.add_signal_receiver(self.property_modified,
                        'PropertyModified', 'org.freedesktop.Hal.Device',
                        'org.freedesktop.Hal', udi, path_keyword='udi')
                    else:
                        mountpoint = dev.GetProperty('volume.mount_point')
                        # TODO: Is the most appropriate check?
                        if mountpoint and os.path.exists('%s/.disk/info' % mountpoint):
                            self.cds[udi] = {
                                'label' : str(dev.GetProperty('volume.label')),
                                'uuid' : str(dev.GetProperty('volume.uuid')),
                                'mountpoint' : mountpoint,
                                'udi' : udi,
                                'size' : dev.GetProperty('volume.size'),
                                'filename' : '',
                            }
                            self.frontend.add_source(udi)
        # USB disks
        devices = self.hal.FindDeviceByCapability('storage')
        for device in devices:
            dev_obj = self.bus.get_object('org.freedesktop.Hal', device)
            d = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
            # Only check physical storage devices (not partitions)
            if not self.IsStorageDevice(d):
                continue
            # Check if this device has a filesystem but no partitions.
            if d.GetProperty('block.is_volume'):
                if d.GetProperty('volume.fstype') == 'vfat':
                    self.add_device(d) 
            else:
                # If not, find all of this device's child partitions
                children = self.hal.FindDeviceStringMatch('info.parent', device)
                c = False
                for child in children:
                    dev_obj = self.bus.get_object('org.freedesktop.Hal', child)
                    child = dbus.Interface(dev_obj, 'org.freedesktop.Hal.Device')
                    if child.GetProperty('block.is_volume'):
                        if child.GetProperty('volume.fstype') == 'vfat':
                            c = True
                            self.add_device(child)
                # If no partitions were found, check for an empty partition table.
                if not c and d.PropertyExists('storage.removable.media_size'):
                    udi = d.GetProperty('info.udi')
                    device = str(d.GetProperty('block.device'))
                    self.devices[device] = {
                        'label' : '',
                        'fstype' : '',
                        'uuid' : '',
                        'mountpoint' : '',
                        'udi' : udi,
                        'free' : d.GetProperty('storage.removable.media_size'),
                        'capacity' : d.GetProperty('storage.removable.media_size'),
                        'device' : device
                    }
                    self.frontend.add_dest(device)

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
        # HAL doesn't support loop mounted filesystems and indeed when manually
        # mounted, the device does not appear in d-feet (searching the
        # mountpoint).  So we have to just manually construct the addition to
        # self.devices.
        self.log('mounting %s' % filename)
        tmpdir = tempfile.mkdtemp()
        res = popen(['mount', '-t', 'iso9660', '-o', 'loop,ro', filename, tmpdir])
        if res[0].returncode:
            self.log('unable to mount %s to %s' % (filename, tmpdir))
            self.log(res[1])
            self.frontend.notify(_('Unable to mount the image %s.\n\n'
                'Please see ~/.usb-creator.log for more details') % filename)
            return
        fp = None
        try:
            fp = open('%s/.disk/info' % tmpdir)
            line = fp.readline().strip('\0')
            line = ' '.join(line.split(' ')[:2])
            size = os.stat(filename).st_size
            self.cds[filename] = { 'label' : line,
                                   'uuid' : '',
                                   'udi' : '',
                                   'mountpoint' : '',
                                   'filename' : filename,
                                   'size' : size }
            self.frontend.add_source(filename)
        except Exception, e:
            self.log('Unable to find %s/.disk/info, not using %s' %
                (tmpdir, filename))
            self.log(str(e))
            self.frontend.notify(_('This is not a desktop install CD and '
                'thus cannot be used by this application.'))
            return
        finally:
            if fp:
                fp.close()
            popen(['umount', tmpdir])
            popen(['rmdir', tmpdir])

    def install_bootloader(self):
        # TODO: Needs to be moved into the generic install routine.
        
        # Ugly, i18n.
        self.frontend.progress(0, _('Installing the bootloader'))
        import re
        device = self.install_target['device']
        udi = self.install_target['udi']
        dev_obj = self.bus.get_object("org.freedesktop.Hal", udi)
        dev = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        dev_obj = self.bus.get_object("org.freedesktop.Hal", dev.GetProperty('info.parent'))
        dev = dbus.Interface(dev_obj, "org.freedesktop.Hal.Device")
        rootdev = dev.GetProperty('block.device')
        tmp = device.lstrip(rootdev)
        match = re.match('.*([0-9]+)$', tmp)
        num = None
        if match:
            num = match.groups()[0]
        self.log('Marking partition %s as active.' % num)
        if not num:
            self.frontend.failed(_('Unable to determine the partition number.'))

        # Install the bootloader to the MBR.
        self.log('installing the bootloader to %s.' % rootdev)
        process = popen(['dd', 'if=/usr/lib/syslinux/mbr.bin',
            'of=%s' % rootdev, 'bs=446', 'count=1', 'conv=sync'])
        bootloader_failed = _('Error installing the bootloader.')
        if process[0].returncode:
            self.frontend.failed(bootloader_failed)
        self.log('installing the bootloader to %s.' % device)
        args = ['syslinux']
        if 'USBCREATOR_SAFE' in os.environ:
            args.append('-s')
        args.append(device)
        process = popen(args)[0]
        if process.returncode:
            self.frontend.failed(bootloader_failed)
        popen(['parted', '-s', rootdev, 'set', num, 'boot', 'on'])

    def copy_files(self):
        tmpdir = ''
        def _copy_files(source, target, persist):
            cmd = ['/usr/share/usb-creator/install.py', '-s', '%s/.' % source,
                '-t', '%s' % target, '-p', '%d' % persist]
            self.log(cmd)
            self.pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=sys.stderr, universal_newlines=True)
            self.watch = gobject.io_add_watch(self.pipe.stdout,
                     gobject.IO_IN | gobject.IO_HUP,
                     self.data_available)
            # Wait for the process to complete
            gobject.child_watch_add(self.pipe.pid, self.on_end)

        source = self.cds[self.install_source]
        if not source['udi']:
            tmpdir = tempfile.mkdtemp()
            popen(['mount', '-o', 'loop,ro', self.install_source, tmpdir])
            source['mountpoint'] = tmpdir
        elif not source['mountpoint']:
            tmpdir = tempfile.mkdtemp()
            popen(['mount', '-o', 'ro', self.install_source, tmpdir])
            source['mountpoint'] = tmpdir
        if not self.install_target['mountpoint']:
            tmpdir = tempfile.mkdtemp()
            popen(['mount', self.install_target['device'], tmpdir])
            self.install_target['mountpoint'] = tmpdir

        # We don't care about updating the main window anymore.
        for timeout in self.timeouts.itervalues():
            gobject.source_remove(timeout)
        self.timeouts = {}
        self.bus.remove_signal_receiver(self.property_modified)
        # Remove files we're going to copy.
        t = self.install_target['mountpoint']
        for obj in os.listdir(self.cds[self.install_source]['mountpoint']):
            obj = os.path.join(t, obj)
            popen(['rm', '-rf', obj])
        popen(['rm', os.path.join(t, 'casper-rw')])
        self.original_size = free_space(self.install_target['mountpoint'])
        _copy_files(source['mountpoint'], self.install_target['mountpoint'],
            self.persistence_size)

    def shutdown(self):
        self.log('Forcing shutdown of the install process.')
        import signal
        try:
            if self.pipe:
                os.kill(self.pipe.pid, signal.SIGTERM)
        except OSError:
            pass
        source = self.cds[self.install_source]
        if source['mountpoint'].startswith('/tmp'):
            self.log('Unmounting source volume.')
            popen(['umount', source['mountpoint']])
            popen(['rmdir', source['mountpoint']])
        if self.install_target['mountpoint'].startswith('/tmp'):
            self.log('Unmounting target volume.')
            popen(['umount', self.install_target['mountpoint']])
            popen(['rmdir', self.install_target['mountpoint']])

    def quit(self):
        for dev in self.devices:
            mp = self.devices[dev]['mountpoint']
            if mp and mp.startswith('/tmp'):
                popen(['umount', mp])
                popen(['rmdir', mp])

    def on_end(self, pid, error_code):
        source = self.cds[self.install_source]
        if source['mountpoint'].startswith('/tmp'):
            self.log('Unmounting source volume.')
            popen(['umount', source['mountpoint']])
            popen(['rmdir', source['mountpoint']])
        if self.install_target['mountpoint'].startswith('/tmp'):
            self.log('Unmounting target volume.')
            popen(['umount', self.install_target['mountpoint']])
            popen(['rmdir', self.install_target['mountpoint']])
        self.log('Install command exited with code: %d' % error_code)
        if error_code != 0:
            self.frontend.failed()
        # TODO: Needed?
        #gobject.source_remove(self.watch)
        self.frontend.finished()

    def copy_progress(self):
        now = free_space(self.install_target['mountpoint'])
        source = float(self.cds[self.install_source]['size'])
        source = source + self.persistence_size
        per = ((self.original_size - now) / source) * 100
        self.frontend.progress(per, self.progress_description)
        return True

    def data_available(self, source, condition):
        text = source.readline()
        if len(text) > 0:
            self.progress_description = text.strip('\n')
            if not self.copy_timeout:
                self.copy_timeout = gobject.timeout_add(2000, self.copy_progress)
            return True
        else:
            if self.copy_timeout:
                gobject.source_remove(self.copy_timeout)
            return False

    def IsStorageDevice(self, d):
        # We only care about usb devices currently
        if d.GetProperty('storage.bus') not in ['usb', 'mmc']:
            return False
        
        # Card readers are not removable, so nix this test.
        #if d.GetProperty('storage.removable') == False:
        #    return False

        # Known good drive types
        drive_types = ['disk',
                       'sd_mmc',
                       'smart_media',
                       'memory_stick',
                       'compact_flash']
        if d.GetProperty('storage.drive_type') in drive_types:
            return True

