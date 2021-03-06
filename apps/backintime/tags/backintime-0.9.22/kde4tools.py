#    Back In Time
#    Copyright (C) 2008-2009 Oprea Dan
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os
import os.path

from PyQt4.QtGui import *
from PyQt4.QtCore import *


def get_font_bold( font ):
	font.setWeight( QFont.Bold )
	return font


def set_font_bold( widget ):
	widget.setFont( get_font_bold( widget.font() ) )


def clipboard_set_path( app, path ):
	mime_data = QMimeData()
	mime_data.setText( path )
	mime_data.setUrls( [ QUrl( path ) ] )

	#gnome copy mime
	mime_data.setData( 'x-special/gnome-copied-files', QString( 'copy\nfile://' + path ).toAscii() )

	clipboard = app.clipboard()
	clipboard.setMimeData( mime_data )

