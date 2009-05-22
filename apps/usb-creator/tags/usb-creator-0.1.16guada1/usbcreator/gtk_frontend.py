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

import sys
import os

from usbcreator.backend import Backend
import gettext
import locale
import pygtk
import gtk.glade
import gobject
import dbus
import gnomevfs

MIN_PERSIST = 128 * 1024 * 1024 # The minimal size, in bytes, that a persistence file can be.
LOCALEDIR = "/usr/share/locale"

#class GtkFrontend(Frontend):
class GtkFrontend:
    def __init__(self,iso=None,persistent=True):
        self.YES, self.MAYBE, self.NO = range(3)

        locale.setlocale(locale.LC_ALL, '')
        for module in gtk.glade, gettext:
            module.bindtextdomain('usbcreator', LOCALEDIR)
            module.textdomain('usbcreator')

        import __builtin__
        __builtin__._ = gettext.gettext

        self.all_widgets = set()

        self.glade = gtk.glade.XML('/usr/share/usb-creator/usbcreator.glade')
        for widget in self.glade.get_widget_prefix(""):
            # Taken from ubiquity:
            # We generally want labels to be selectable so that people can
            # easily report problems in them
            # (https://launchpad.net/bugs/41618), but GTK+ likes to put
            # selectable labels in the focus chain, and I can't seem to turn
            # this off in glade and have it stick. Accordingly, make sure
            # labels are unfocusable here.
            if isinstance(widget, gtk.Label):
                widget.set_property('can-focus', False)
            self.all_widgets.add(widget)
            setattr(self, widget.get_name(), widget)

        self.backend = Backend(self)

        gtk.window_set_default_icon_from_file('/usr/share/pixmaps/usb-creator.png')
        self.glade.signal_autoconnect(self)
        self.cancelbutton.connect('clicked', lambda x: self.warning_dialog.hide())
        self.exitbutton.connect('clicked', lambda x: self.abort())
        self.progress_cancel_button.connect('clicked', lambda x: self.warning_dialog.show())
        def format_value(scale, value):
            return format_size(value)
        self.persist_value.set_adjustment(
            gtk.Adjustment(0, 0, 100, 1, 10, 0))
        self.persist_value.connect('format-value', format_value)

        self.setup_source()
        self.setup_dest()
        m = self.dest_treeview.get_model()
        self.update_row_state(m, None)
        self.persist_vbox.set_sensitive(False)
        self.button_install.set_sensitive(False)
        self.backend.detect_devices()
        self.window.show()
        
        if iso is not None:
            self.backend.mount_iso(iso)
        
        if not persistent:
            self.persist_disabled.set_active(True)

        gtk.main()

    def abort(self, *args):
        self.backend.shutdown()
        sys.exit(0)

    def quit(self, *args):
        self.backend.quit()
        sys.exit(0)

    def failed(self, title=None):
        self.backend.shutdown()
        self.warning_dialog.hide()
        self.install_window.hide()
        if title:
            self.failed_dialog_label.set_text(title)
            self.backend.log('Install failed: ' + title)
        else:
            self.backend.log('Install failed.')
        self.failed_dialog.run()
        sys.exit(1)
    
    def finished(self, *args):
        self.warning_dialog.hide()
        self.install_window.hide()
        label = self.finished_dialog_label.get_text()
        self.finished_dialog_label.set_text(label % "Guadalinex")
        self.finished_dialog.run()
        sys.exit(0)

    def notify(self, message):
        dialog = gtk.MessageDialog(None, 0, gtk.MESSAGE_WARNING,
            gtk.BUTTONS_CLOSE, message)
        dialog.run()
        dialog.destroy()

    def format_dest_clicked(self, *args):
        model, iterator = self.dest_treeview.get_selection().get_selected()
        if not iterator:
            return
        disk = model[iterator][0]
        self.backend.format_device(disk)

    def open_dest_folder(self, *args):
        # TODO: This should really call whatever GNOME does when you click on
        # the device in the places menu, so the device gets mounted if it isn't
        # already.
        # TODO: Should use something neutral as XFCE could also use the GTK
        # frontend.
        model, iterator = self.dest_treeview.get_selection().get_selected()
        if not iterator:
            return
        disk = model[iterator][0]
        mp = self.backend.devices[disk]['mountpoint']
        if mp:
            cmd = ['gnome-open', mp]
            from usbcreator.backend import popen
            popen(cmd)

    def add_source(self, source):
        ni = self.source_treeview.get_model().append([source])
        sel = self.source_treeview.get_selection()
        m, i = sel.get_selected()
        if not i:
            sel.select_iter(ni)

    def device_removed(self, d, source):
        '''The backend has removed a device from its list and the frontend now
        needs to do the same.

        Keyword arguments:
        d      -- the key (a udi string) of the item to delete.
        source -- if True, then the frontend needs to remove a source device
                  (CD), otherwise it needs to remove a destination device (USB
                  drive).
        '''
        # TODO: Maybe split this in half?
        to_delete = None
        if source:
            m = self.source_treeview.get_model()
        else:
            m = self.dest_treeview.get_model()
        iterator = m.get_iter_first()
        while iterator is not None:
            if m.get_value(iterator, 0) == d:
                to_delete = iterator
                self.backend.log('deleting %s from the ui' % d)
            iterator = m.iter_next(iterator)
        if to_delete is not None:
            m.remove(to_delete)
        if len(m) == 0:
            self.backend.log('device removed and none left.  source = %s' % str(source))
            self.persist_vbox.set_sensitive(False)
            self.button_install.set_sensitive(False)

    def update_all_rows(self, selection):
        m = self.dest_treeview.get_model()
        iterator = m.get_iter_first()
        while iterator is not None:
            self.update_row_state(m, iterator)
            iterator = m.iter_next(iterator)

        # TODO: Disabled for now, re-evaluate as testing allows.  Initial
        # testing looks OK.
        #sel = self.dest_treeview.get_selection()
        #self.dest_selection_changed(sel)

    def get_gnome_drive(self, udi):
        monitor = gnomevfs.VolumeMonitor()
        for drive in monitor.get_connected_drives():
            if drive.get_hal_udi() == udi:
                return drive

    def setup_source(self):
        def column_data_func(column, cell, model, iterator, pos):
            val = model[iterator][0]
            dev = self.backend.cds[val]
            if pos == 0:
                if dev['udi']:
                    drive = self.get_gnome_drive( dev['udi'] )
                    if drive:
                        cell.set_property('text', drive.get_display_name())
                    else:
                        cell.set_property('text', dev['mountpoint'])
                else:
                    cell.set_property('text', dev['filename'])
            elif pos == 1:
                cell.set_property('text', dev['label'])
            elif pos == 2:
                cell.set_property('text', format_size(dev['size']))

        def pixbuf_data_func(column, cell, model, iterator):
            dev = self.backend.cds[model[iterator][0]]
            drive = self.get_gnome_drive( dev['udi'] )
            if drive:
                cell.set_property('icon-name', drive.get_icon())
            else:
                cell.set_property('stock-id', None)


        # TODO: Drag and drop support.  Should be over the entire window.
        list_store = gtk.ListStore(str)
        self.source_treeview.set_model(list_store)

        cell_name = gtk.CellRendererText()
        cell_pixbuf = gtk.CellRendererPixbuf()
        column_name = gtk.TreeViewColumn(_('CD-Drive/Image'))
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column_name.pack_start(cell_pixbuf, expand=False)
        column_name.pack_start(cell_name, expand=True)
        self.source_treeview.append_column(column_name)
        column_name.set_cell_data_func(cell_name, column_data_func, 0)
        column_name.set_cell_data_func(cell_pixbuf, pixbuf_data_func)

        cell_version = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_('OS Version'), cell_version)
        column_name.set_cell_data_func(cell_version, column_data_func, 1)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.source_treeview.append_column(column_name)

        cell_size = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_('Size'), cell_size)
        column_name.set_cell_data_func(cell_size, column_data_func, 2)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.source_treeview.append_column(column_name)

        selection = self.source_treeview.get_selection()
        selection.connect('changed', self.update_all_rows)

    def select_iso(self, *args):
        filename = ''
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.add_pattern('*.iso')
        # TODO: i18n
        filter.set_name(_('ISO Files'))
        chooser.add_filter(filter)
        if 'SUDO_USER' in os.environ:
            folder = os.path.expanduser('~' + os.environ['SUDO_USER'])
        else:
            folder = os.path.expanduser('~')
        chooser.set_current_folder(folder)
        response = chooser.run()
        failed = False
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.backend.mount_iso(filename)
        chooser.destroy()

    def add_dest(self, dest):
        self.backend.log('adding: %s' % dest)
        ni = self.dest_treeview.get_model().append([dest, self.YES])
        sel = self.dest_treeview.get_selection()
        m, i = sel.get_selected()
        if not i:
            sel.select_iter(ni)

    def update_row_state(self, model, iterator):
        m, i = self.source_treeview.get_selection().get_selected()
        if not i:
            self.source_status.set_text(_('Please insert a CD or select \'Other...\'.'))
        else:
            self.source_status.set_text('')
        if not iterator:
            self.open_dest.hide()
            self.format_dest.hide()
            self.dest_status.set_text(_('Please insert a USB stick.'))
            iterator = model.get_iter_first()
            while iterator is not None:
                model[iterator][1] = self.YES
                iterator = model.iter_next(iterator)
        else:
            self.dest_status.set_text('')
        if not i or not iterator:
            # There's no selection, which means one of the treeviews is empty.
            return

        cd = self.backend.cds[m[i][0]]
        disk = model[iterator][0]
        disk = self.backend.devices[disk]

        # Disk
        if not disk['fstype']:
            if cd['size'] > disk['capacity']:
                model[iterator][1] = self.NO
            else:
                model[iterator][1] = self.MAYBE
        # Partition
        else:
            if cd['size'] < disk['free']:
                model[iterator][1] = self.YES
            elif cd['size'] > disk['capacity']:
                model[iterator][1] = self.NO
            else:
                model[iterator][1] = self.MAYBE

        if self.dest_treeview.get_selection().iter_is_selected(iterator):
            self.backend.log('updating dest_status as part of update_row_state')
            self.open_dest.hide()
            self.format_dest.hide()
            self.button_install.set_sensitive(False)
            # Disk
            if not disk['fstype']:
                if cd['size'] > disk['capacity']:
                    self.dest_status.set_text(_('%s is too small for %s.') % \
                        (disk['device'], cd['label']))
                else:
                    self.dest_status.set_text(_('%s needs to be formatted.') % \
                        disk['device'])
                    self.format_dest.show()
            # Partition
            else:
                if cd['size'] < disk['free']:
                    self.dest_status.set_text(
                        _('%s has enough free space for %s.') % \
                        (disk['device'], cd['label']))
                    self.button_install.set_sensitive(True)
                    self.persist_vbox.set_sensitive(True)
                    persist_max = disk['free'] - cd['size']
                    if persist_max > MIN_PERSIST:
                        self.persist_vbox.set_sensitive(True)
                        self.persist_enabled_vbox.set_sensitive(True)
                        self.persist_value.set_range(MIN_PERSIST, persist_max)
                    else:
                        self.persist_enabled_vbox.set_sensitive(False)
                        self.persist_disabled.set_active(True)
                elif cd['size'] > disk['capacity']:
                    self.dest_status.set_text(_('%s is too small for %s.') % \
                        (disk['device'], cd['label']))
                else:
                    needed = cd['size'] - disk['free']
                    needed = format_size(needed)
                    # TODO: Can we size the window at startup to fix this
                    # string and the button?
                    self.dest_status.set_text(
                        _('%s is too full to fit %s (%s more needed).') % \
                        (disk['device'], cd['label'], needed))
                    self.open_dest.show()

    def update_dest_row(self, device):
        m = self.dest_treeview.get_model()
        iterator = m.get_iter_first()
        while iterator is not None:
            if m.get_value(iterator, 0) == device:
                self.update_row_state(m, iterator)
                m.row_changed(m.get_path(iterator), iterator)
                break
            iterator = m.iter_next(iterator)

    def dest_selection_changed(self, selection):
        model, iterator = selection.get_selected()
        self.update_row_state(model, iterator)

    def setup_dest(self):
        def column_data_func(column, cell, model, iterator, pos):
            val = model[iterator][0]
            dev = self.backend.devices[val]
            drive = self.get_gnome_drive( dev['udi'] )
            if pos == 0:
                if drive:
                    cell.set_property('text', drive.get_display_name() )
                else:
                    cell.set_property('text', dev['device'])
            elif pos == 1:
                cell.set_property('text', dev['label'])
            elif pos == 2:
                cell.set_property('text', format_size(dev['capacity']))
            elif pos == 3:
                cell.set_property('text', format_size(dev['free']))
        def pixbuf_data_func(column, cell, model, iterator):
            if model[iterator][1] == self.MAYBE:
                cell.set_property('stock-id', gtk.STOCK_DIALOG_WARNING)
            elif model[iterator][1] == self.NO:
                # TODO: Implement disabled rows as a replacement?
                cell.set_property('stock-id', gtk.STOCK_DIALOG_ERROR)
            else:
                dev = self.backend.devices[model[iterator][0]]
                drive = self.get_gnome_drive( dev['udi'] )
                if drive:
                    cell.set_property('icon-name', drive.get_icon())
                else:
                    cell.set_property('stock-id', None)

        list_store = gtk.ListStore(str, int)
        self.dest_treeview.set_model(list_store)

        column_name = gtk.TreeViewColumn()
        column_name.set_title(_('Device'))
        cell_name = gtk.CellRendererText()
        cell_pixbuf = gtk.CellRendererPixbuf()
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        column_name.pack_start(cell_pixbuf, expand=False)
        column_name.pack_start(cell_name, expand=True)
        self.dest_treeview.append_column(column_name)
        column_name.set_cell_data_func(cell_name, column_data_func, 0)
        column_name.set_cell_data_func(cell_pixbuf, pixbuf_data_func)
        
        cell_name = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_('Label'), cell_name)
        column_name.set_cell_data_func(cell_name, column_data_func, 1)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.dest_treeview.append_column(column_name)

        cell_capacity = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_('Capacity'), cell_capacity)
        column_name.set_cell_data_func(cell_capacity, column_data_func, 2)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.dest_treeview.append_column(column_name)

        cell_free = gtk.CellRendererText()
        column_name = gtk.TreeViewColumn(_('Free Space'), cell_free)
        column_name.set_cell_data_func(cell_free, column_data_func, 3)
        column_name.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        self.dest_treeview.append_column(column_name)

        selection = self.dest_treeview.get_selection()
        selection.connect('changed', self.dest_selection_changed)

    def install(self, widget):
        self.backend.log('Installing...')
        self.window.hide()
        starting_up = _('Starting up')
        self.progress_title.set_markup('<big><b>' + starting_up + '</b></big>')
        self.progress_info.set_text('')
        self.install_window.show()
        m, i = self.source_treeview.get_selection().get_selected()
        if not i:
            self.failed(_('Install button pressed but there was no source selected.'))
        val = m[i][0]
        self.backend.log('Source CD: %s' % val)
        self.backend.set_install_source(val)
        m, i = self.dest_treeview.get_selection().get_selected()
        if not i:
            self.failed(_('Install button pressed but there was no destination selected.'))
        val = m[i][0]
        self.backend.log('Destination disk: %s' % val)
        self.backend.set_install_target(val)
        if self.persist_enabled.get_active():
            val = int(self.persist_value.get_value())
        else:
            val = 0
        self.backend.log('Persistence size: %d B' % val)
        self.backend.set_persistence_size(val)
        self.backend.install_bootloader()
        try:
            self.backend.copy_files()
        except Exception, e:
            self.failed(str(e))

    def progress(self, val, desc):
        self.progress_info.set_text(_('%d%% complete') % val)
        self.progress_bar.set_fraction(val / 100.0)
        self.progress_title.set_markup('<big><b>' + desc + '</b></big>')

def format_size(size):
    """Format a partition size."""
    # Taken from ubiquity's ubiquity/misc.py
    if size < 1024:
        unit = 'B'
        factor = 1
    elif size < 1024 * 1024:
        unit = 'kB'
        factor = 1024
    elif size < 1024 * 1024 * 1024:
        unit = 'MB'
        factor = 1024 * 1024
    elif size < 1024 * 1024 * 1024 * 1024:
        unit = 'GB'
        factor = 1024 * 1024 * 1024
    else:
        unit = 'TB'
        factor = 1024 * 1024 * 1024 * 1024
    return '%.1f %s' % (float(size) / factor, unit)

# vim: set ai et sts=4 tabstop=4 sw=4:
