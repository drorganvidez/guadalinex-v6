# -*- coding: utf-8 -*-
#
# Authors:
#     Original creators of hermes v1: Unknown
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo principal coldassistant - Controlador de ventana GTK para el 
#      asistente en frio
# [en] coldassistant main module - Coldassistant GTK window manager
#
# Copyright (C) 2009 Junta de Andalucía
#
# ----------------------------[es]---------------------------------------------
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
# ----------------------------[en]---------------------------------------------
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



import sys
sys.path.insert(0, './')

import gtk
import gtk.glade
import gettext

from hermes_hardware import setup_gettext
from devicelist import DeviceList


class Controller(object):
    """ 
    [es] Clase básica para la creación de una ventana GTK para el Asistente
         en frio. Desde esta ventana podremos ver dispositivos reconocidos por 
         hermes
    ---------------------------------------------------------------------------
    [en] Basic class to create a GTK window for coldassistant. From this window
         we can see hermes recognized devices
    """
    def __init__(self):
        """ 
        [es] Inicialización de la aplicacion GTK
        -----------------------------------------------------------------------
        [en] GTK app initialization
        """
        xml = gtk.glade.XML('coldassistant/ui.glade', root='mainwindow')
        xml.signal_autoconnect(self)

        self.window = xml.get_widget('mainwindow')
        self.finalize = False

#        icon = gtk.gdk.pixbuf_new_from_file("/usr/share/hermes/img/logo.svg")
        icon = gtk.gdk.pixbuf_new_from_file("img/logo.svg")
        self.window.set_icon(icon)

        vbox = xml.get_widget('treeview_vbox')

        devicelist = DeviceList()
        vbox.pack_start(devicelist, False, False)
        self.devicelist = devicelist


    def reset(self):
        self.devicelist.reset()
        """ 
        [es] Captura de evento de actualización de lista de dispositivos
        -----------------------------------------------------------------------
        [en] Device list refresh event handling
        """

    def on_close_clicked(self, widget):
        """ 
        [es] Captura de evento de cierre de ventana
        -----------------------------------------------------------------------
        [en] Close window event handling
        """
        self.finalize = True
        gtk.main_quit()



if __name__ == '__main__':
    try:
        import defs
        setup_gettext('hermes-hardware', defs.DATA_DIR)
    except ImportError:
        print 'WARNING: Running uninstalled, no gettext support'

    controller = Controller()
    while not controller.finalize:
        controller.reset()
        gtk.main()
