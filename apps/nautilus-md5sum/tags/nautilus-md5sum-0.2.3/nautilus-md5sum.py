#!/usr/bin/env python
# David Amian y Alvaro Pinel 

import md5
import urllib
import os
import gtk
import nautilus
import time
import ConfigParser
import sys
import mimetypes

FORMAT = ["application/x-cd-image"]

## locate in /usr/lib/nautilus/extension-2.0/python/

def alert(message):
    """Shows an alert with the text 'message'."""
    dialog = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)
    dialog.run()
    dialog.destroy()
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

		alert(md5.md5(filename).hexdigest())
