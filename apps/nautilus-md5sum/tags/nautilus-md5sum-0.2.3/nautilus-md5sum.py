#!/usr/bin/env python
# -*- encoding: utf-8 -*-

# David Amián Valle y Álvaro Pinel Bueno


import md5
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



def alert(message,dialogP):
    """Shows an alert with the text 'message'."""
    dialog = gtk.Dialog("nautilus-md5sum",dialogP, gtk.DIALOG_DESTROY_WITH_PARENT)
    dialog.set_border_width(10)
    label=gtk.Label(message)
    label.show()
    button1=gtk.Button("Ok",gtk.STOCK_OK)
    button1.connect_object("clicked", gtk.Widget.destroy, dialogP)
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
		file = files[0]

		if file.get_mime_type() not in FORMAT:
			return

		items=[]
		"""Called when the user selects a file in Nautilus."""
		item = nautilus.MenuItem("NautilusPython::md5sum_item", "Calcular suma MD5", "Calcular suma MD5")
		item.connect("activate", self.menu_activate_cb, files)
		items.append(item)
		return items

	def menu_activate_cb(self, menu, files):
		"""Called when the user selects the menu."""
		if len(files) != 1:
	            return
               	file = files[0]
		if file.get_uri_scheme() != 'file':
	            return

        	if file.is_directory():
	            return

        	filename = urllib.unquote(file.get_uri()[7:])

		dialog = gtk.Dialog("nautilus-md5sum")
		dialog.set_border_width(10)
		label=gtk.Label("El calculo de la suma MD5 puede tardar varios \nminutos dependiendo del tamaño de la imágen de disco")
    		label.show()
    		button1=gtk.Button("Ok",gtk.STOCK_OK)
    		button1.connect_object("clicked", alert, "La suma MD5 es:\n\n"+md5.md5(filename).hexdigest(),dialog)
    		button1.show()
    		dialog.vbox.pack_start(label)
    		dialog.action_area.pack_start(button1)
    		dialog.show()

		#alert("El calculo de la suma MD5 puede tardar varios \nminutos dependiendo del tamaño de la imágen de disco")
		
