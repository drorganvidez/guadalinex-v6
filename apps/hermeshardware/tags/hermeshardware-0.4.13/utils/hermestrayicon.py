# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo hermestrayicon -
# [en] hermestrayicon module -
#
# Copyright (C) 2009 Junta de Andalucía
# 
# ----------------------------[es]----------------------------- 
#
# Este fichero es parte de Detección de Hardware de Guadalinex V6 
# 
# Este programa es software libre: puede redistribuirlo y/o modificarlo bajo 
# los términos de la Licencia Pública General version 3 de GNU según 
# es publicada por la Free Software Foundation.
# 
# Este programa se distribuye con la esperanza de que será útil, pero 
# SIN NINGUNA GARANTÍA, incluso sin la garantías implicitas de 
# MERCANTILIZACION, CALIDAD SATISFACTORIA o de CONVENIENCIA PARA UN PROPÓSITO 
# PARTICULAR. Véase la Licencia Pública General de GNU para más detalles. 
# 
# Debería haber recibido una copia de la Licencia Pública General 
# junto con este programa; si no ha sido así, 
# visite <http://www.gnu.org/licenses/>
# o escriba a la Free Software Foundation, Inc., 
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA.
# 
# ----------------------------[en]----------------------------- 
# 
# This file is part of Guadalinex V6 Hardware Detection.
#
# This program is free software: you can redistribute it and/or modify it      
# under the terms of the GNU General Public License version 3, as published    
# by the Free Software Foundation.                                             
#                                                                              
# This program is distributed in the hope that it will be useful, but          
# WITHOUT ANY WARRANTY; without even the implied warranties of                 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR           
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, visit <http://www.gnu.org/licenses/>
# or write to the Free Software Foundation, Inc., 
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import os
import sys

import gtk
import gobject
from egg.trayicon import TrayIcon

class HermesTrayIcon(TrayIcon):
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """
    def __init__(self):
        TrayIcon.__init__(self, 'Hermes TrayIcon')

        # Set up icon 
        self.button = gtk.Button()
        self.button.set_relief(gtk.RELIEF_NONE)
        event_box = gtk.EventBox()
        event_box.connect("button-press-event", self.on_mouse_press)
        image = gtk.Image()
        event_box.add(image)
        image.set_from_file('/home/pchaso/dev/hermes2/img/logo_16.png')
        self.add(event_box)

        # Set up menu
        self.menu = HermesMenu()

        self.show_all()


    def on_mouse_press(self, widget, event):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        if event.button == 3:
            self.menu.popup(None, None, None,
                    event.button, event.time)
            self.menu.show_all()

        elif event.button ==  1:
            self.menu.on_open()

        return True



class HermesMenu(gtk.Menu):
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """
    def __init__(self):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        gtk.Menu.__init__(self)

        self._configure()


    def _configure(self):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        # Open coldassistant
        item = gtk.MenuItem('Abrir el asistente de acciones')
        item.connect('activate', self.on_open)
        self.append(item)

        # Separator
        self.append(gtk.SeparatorMenuItem())

        # Quit option
        quit_item = gtk.ImageMenuItem(stock_id = gtk.STOCK_QUIT)
        quit_item.connect('activate', self.on_quit)
        self.append(quit_item)


    def on_quit(self, widget):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        gtk.main_quit()
        sys.exit(0)


    def on_open(self, widget = None):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.get_screen().get_root_window().set_cursor(cursor)
        os.system('hcoldassistant &')
        gobject.timeout_add(2000, self.__timeout)


    def __timeout(self):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        self.get_screen().get_root_window().set_cursor(cursor)
        # Exit loop
        return False

