#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# David Amián y Álvaro Pinel 


import urllib
import os
import gtk
import nautilus
import time
import ConfigParser
import sys
import mimetypes
import pygtk
# We use the 2.0 gtk version
pygtk.require('2.0')

FORMAT = ["application/x-cd-image"]

## locate in /usr/lib/nautilus/extension-2.0/python/


def calculateMD5(message, filename, dialogP):
    """Shows an alert with the text 'message'."""
    dialog = gtk.Dialog("nautilus-md5sum",
                         dialogP,
                         gtk.DIALOG_DESTROY_WITH_PARENT)
    dialog.set_border_width(10)
    res = os.popen("md5sum %s" % filename).read()
    result = res.split('/')[0]
    label = gtk.Label(message+result)
    label.show()
    button1 = gtk.Button("Ok", gtk.STOCK_OK)
    button1.connect_object("clicked",
                            gtk.Widget.destroy,
                            dialogP)
    button1.show()
    dialog.vbox.pack_start(label)
    dialog.action_area.pack_start(button1)
    dialog.show()
    
    return 
    


class MD5Extension(nautilus.MenuProvider):
    def __init__(self):
        pass
    
    def get_file_items(self, window, files):

        if len(files)!=1:
            return
        filename = files[0]

        if filename.get_mime_type() not in FORMAT:
            return

        items = []
        """Called when the user selects a file in Nautilus."""
        item = nautilus.MenuItem("NautilusPython::md5sum_item",
                                 "Calcular suma MD5",
                                 "Calcular suma MD5")
        item.connect("activate", self.menu_activate_cb, files)
        items.append(item)
        return items

    def menu_activate_cb(self, menu, files):
        """Called when the user selects the menu."""
        if len(files) != 1:
            return
        filename = files[0]
        if filename.get_uri_scheme() != 'file':
            return

        if filename.is_directory():
            return

        filename = urllib.unquote(filename.get_uri()[7:])

        dialog = gtk.Dialog("nautilus-md5sum")
        dialog.set_border_width(10)
        label = gtk.Label("El calculo de la suma MD5 puede tardar varios \n" +
                          "minutos dependiendo del tamaño de la imágen de disco")
        label.show()
        button1 = gtk.Button("Ok", gtk.STOCK_OK)
        button1.connect_object("clicked",
                               calculateMD5,
                               "La suma MD5 es:\n\n",
                               filename,
                               dialog)
        button1.show()
        dialog.vbox.pack_start(label)
        dialog.action_area.pack_start(button1)
        dialog.show()

