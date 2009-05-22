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

import sys
import os

from usbcreator.backend import Backend
#from usbcreator.frontend.base import Frontend

import pygtk
import gtk.glade
import gobject
import dbus

#class GtkFrontend(Frontend):
class GtkFrontend:
    def __init__(self):
        self.all_widgets = set()

        # TODO: Ick.
        self.glade = gtk.glade.XML('/usr/share/usb-creator/usbcreator.glade')
        for widget in self.glade.get_widget_prefix(""):
            self.all_widgets.add(widget)
            setattr(self, widget.get_name(), widget)
            # Taken from ubiquity:
            # We generally want labels to be selectable so that people can
            # easily report problems in them
            # (https://launchpad.net/bugs/41618), but GTK+ likes to put
            # selectable labels in the focus chain, and I can't seem to turn
            # this off in glade and have it stick. Accordingly, make sure
            # labels are unfocusable here.
            if isinstance(widget, gtk.Label):
                widget.set_property('can-focus', False)

        # TODO: lots of i18n work.
        # self.translate_widgets()

        if os.getuid() != 0:
            title = ('This utility must be run with administrative '
                     'privileges, and cannot continue without them.')
            dialog = gtk.MessageDialog(self.window, gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                       title)
            dialog.run()
            sys.exit(1)

        self.backend = Backend(self)
        self.glade.signal_autoconnect(self)
        self.setup_source_combo()
        self.setup_dest_combo()
        # TODO: Implement persistence.
        self.persist_vbox.set_sensitive(False)
        self.backend.detect_devices()
        if self.source_combo.get_active_iter() is None or \
            self.dest_combo.get_active_iter() is None:
            self.button_install.set_sensitive(False)
        self.window.show()
        gtk.main()

    def quit(self, *args):
        sys.exit(0)

    def add_source(self, source):
        # TODO: As we didn't use the convenience function to set it up, we
        # shouldn't use the same set of functions to manipulate it, according
        # to the documentation.
        self.source_combo.prepend_text(source)

    def setup_source_combo(self):
        # TODO: selecting a ISO from the menu should call into the backend
        # which will mount it, then process the HAL event in a function that
        # will, in the case of an ISO, tell the frontend to automatically
        # select it.
        # TODO: The function in the frontend that will add a new item to the
        # source combo will need to take care to insert above the 'Select a CD
        # image...' option and the separator above it (ListStore.prepend).
        cd_img = 'Select a CD image...'
        def cell_data_func(celllayout, cell, model, iter):
            val = model.get_value(iter, 0)
            if (val != cd_img and val != '-') and val != None:
                dev = self.backend.source_devices[val]
                cell.set_property('text', dev['title'])
        def row_separator_func(model, iter):
            if model.get_value(iter, 0) == '-':
                return True
            else:
                return False
        def selection_changed(combobox):
            m = combobox.get_model()
            val = m.get_value(combobox.get_active_iter(), 0)
            if val == cd_img:
                filename = self.select_iso()
                iterator = m.get_iter_first()
                while iterator is not None:
                    if m.get_value(iterator, 0) == filename:
                        combobox.set_active_iter(iterator)
                        break
                    iterator = m.iter_next(iterator)
                for val in self.backend.devices.itervalues():
                    s_val = self.backend.source_devices[filename]
                    if val['free'] < s_val['size']:
                        # FIXME:
                        print 'target is too small for source.'
            if self.source_combo.get_active_iter() is not None and \
                self.dest_combo.get_active_iter() is not None:
                self.button_install.set_sensitive(True)
        renderer = gtk.CellRendererText()
        self.source_combo.pack_start(renderer, True)
        self.source_combo.add_attribute(renderer, 'text', 0)
        list_store = gtk.ListStore(gobject.TYPE_STRING)
        self.source_combo.set_model(list_store)
        self.source_combo.set_cell_data_func(renderer, cell_data_func)
        self.source_combo.set_row_separator_func(row_separator_func)
        list_store.append(['-'])
        # TODO: i18n
        list_store.append([cd_img])
        self.source_combo.connect('changed', selection_changed)

    def select_iso(self):
        chooser = gtk.FileChooserDialog(title=None,action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        filter = gtk.FileFilter()
        filter.add_pattern('*.iso')
        # TODO: i18n
        filter.set_name('ISO Files')
        chooser.add_filter(filter)
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.backend.mount_iso(filename)
        chooser.destroy()
        return filename

    def add_dest(self, dest):
        self.dest_combo.append_text(dest)
        if self.dest_combo.get_active_iter() is None:
            m = self.dest_combo.get_model()
            iterator = m.get_iter_first()
            while iterator is not None:
                if m.get_value(iterator, 0) == dest:
                    self.dest_combo.set_active_iter(iterator)
                    break
                iterator = m.iter_next(iterator)

    def setup_dest_combo(self):
        def selection_changed(combobox):
            # TODO: Ensure a vfat filesystem is present.  Make sure there is
            # free space.
            if self.source_combo.get_active_iter() is not None and \
                self.dest_combo.get_active_iter() is not None:
                self.button_install.set_sensitive(True)
        def cell_data_func(celllayout, cell, model, iter):
            model_val = model.get_value(iter, 0)
            if model_val:
                val = self.backend.devices[model_val]
                if val['label']:
                    cell.set_property('text', '%s %s (%s)' % \
                        (val['label'], val['device'], val['uuid']))
                else:
                    cell.set_property('text', '%s (%s)' % \
                        (val['device'], val['uuid']))
        renderer = gtk.CellRendererText()
        self.dest_combo.pack_start(renderer, True)
        self.dest_combo.add_attribute(renderer, 'text', 0)
        list_store = gtk.ListStore(gobject.TYPE_STRING)
        self.dest_combo.set_model(list_store)
        self.dest_combo.set_cell_data_func(renderer, cell_data_func)
        self.dest_combo.connect('changed', selection_changed)

    def install(self, widget):
        print 'Installing...'
        # TODO: Need to do more to tear down.  Kill watches, etc.
        self.window.hide()
        self.install_window.show()
        val = self.source_combo.get_model().get_value( \
            self.source_combo.get_active_iter(), 0)
        self.backend.set_install_source(val)
        val = self.dest_combo.get_model().get_value( \
            self.dest_combo.get_active_iter(), 0)
        self.backend.set_install_target(val)
        self.backend.install_bootloader()
        self.backend.copy_files()

    def progress(self, val):
        self.progress_bar.set_value(val)

# vim: set ai et sts=4 tabstop=4 sw=4:
