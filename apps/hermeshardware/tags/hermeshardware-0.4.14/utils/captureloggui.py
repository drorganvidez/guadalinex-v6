# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo captureloggui - aplicacion que permite obtener un volcado
#      de la informacion proporcionada por un dispositivo USB conectado.
#      Se pretende proporcionar al usuario una herramienta simple para 
#      remitir a los desarrolladores del proyecto Hermes, informacion 
#      util sobre dispositivos no soportados.
# [en] captureloggui module - app that allows the user dumping the
#      information provided by any USB device connected. Pretends to be
#      an easy tool for the end user to send the hermes developer team
#      valuable feedback information about unsupported USB devices.
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



import gtk
import gtk.glade
import sys
import tempfile
import logging
import os.path
import webbrowser

def get_user_dir(key):
    """ 
    [es] Obtiene las rutas completas de los directorios xdg-user-dirs.
         http://www.freedesktop.org/wiki/Software/xdg-user-dirs
            XDG_DESKTOP_DIR
            XDG_DOWNLOAD_DIR
            XDG_TEMPLATES_DIR
            XDG_PUBLICSHARE_DIR
            XDG_DOCUMENTS_DIR
            XDG_MUSIC_DIR
            XDG_PICTURES_DIR
            XDG_VIDEOS_DIR
    -----------------------------------------------------------------------
    [en] Gets the xdg-user-dirs folders complete path.
         http://www.freedesktop.org/wiki/Software/xdg-user-dirs
            XDG_DESKTOP_DIR
            XDG_DOWNLOAD_DIR
            XDG_TEMPLATES_DIR
            XDG_PUBLICSHARE_DIR
            XDG_DOCUMENTS_DIR
            XDG_MUSIC_DIR
            XDG_PICTURES_DIR
            XDG_VIDEOS_DIR
    """
    user_dirs_dirs = os.path.expanduser("~/.config/user-dirs.dirs")
    if os.path.exists(user_dirs_dirs):
        f = open(user_dirs_dirs, "r")
        for line in f.readlines():
            if line.startswith(key):
                return os.path.expandvars(line[len(key)+2:-2])
    return False

xdg_desktop_dir = get_user_dir("XDG_DESKTOP_DIR")
if xdg_desktop_dir and os.path.exists(xdg_desktop_dir):
    desktop_dir = xdg_desktop_dir
else:
    desktop_dir=os.environ['HOME']


class CaptureLogGui(object):
    """ 
    [es] Esta clase se utiliza para crear una ventana en la interfaz de
         usuario desde la que se muestra una lista con todos los 
         dispositivos conectados al puerto USB y permite volcar a un 
         fichero de texto en el escritorio del usuario toda la informacion
         proporcionada por el dispositivo de la lista que se haya
         seleccionado
    -----------------------------------------------------------------------
    [en] This class creates a window on the GUI showing a list with all the 
         USB devices connected and creates a log text file on the user 
         desktop with all the information provided by the device selected
         from the list 
    """

    def __init__(self):
        """ 
        [es] Inicializa la interfaz grafica de usuario para permitir la
             captura de la informacion de los dispositivos USB conectados
        -------------------------------------------------------------------
        [en] Initialize the GUI to allow the logging of the USB devices
             connected information
        """

        self.logger = logging.getLogger()

        # [es] Crea el fichero de registro 
        # [en] Set logfile
        self.__set_logfile()

        # [es] Crea la interfaz de usuario 
        # [en] Set user interface
        xml = gtk.glade.XML('utils/captureloggui.glade', root = 'mainwindow')
        xml.signal_autoconnect(self)

        self.mainwindow = xml.get_widget('mainwindow')
        icon = gtk.gdk.pixbuf_new_from_file("/usr/share/hermes/img/logo.svg")

        self.mainwindow.set_icon(icon)
        self.mainwindow.show_all()
        self.devnameentry = xml.get_widget('devname')


    # [es] Manejadores de se�ales
    # [en] Signal Handlers
    def on_capturelog(self, *args):
        """ 
        [es] Inicia el proceso de captura de la informacion del dispositivo
             conectado al puerto USB cuando el usuario pulsa el boton de 
             inicio de captura de la interfaz grafica de usuario
        -------------------------------------------------------------------
        [en] Starts the USB device information logging process when the
             user clicks the corresponding button from the GUI
        """
        self.logfile.close()

        devname = self.devnameentry.get_text() or 'newdevice'

        content = open(self.logfilepath).read()
        newfile = open(desktop_dir + os.sep + devname + '.log', 'w')

        newfile.write(content)
        newfile.close()

        self.__set_logfile()
        

    def on_cancel(self, *args):
        """ 
        [es] Cuando se recibe la se�al de cancelacion se finaliza la 
             aplicacion
        -------------------------------------------------------------------
        [en] It finishes the application when cancel signal is received
        """
        gtk.main_quit()


    def on_finish(self, *args):
        """ 
        [es] Cuando se recibe la se�al de finalizacion se cierra la 
             aplicacion
        -------------------------------------------------------------------
        [en] It finishes the application when finish signal is received
        """
        gtk.main_quit()


    def on_help_clicked(self, *args):
        """ 
        [es] Cuando se recibe la se�al de ayuda se lanza un navegador web y
             se carga el archivo de ayuda de la documentacion de hermes
        -------------------------------------------------------------------
        [en] It launches a web browser and loads the help file from hermes
             documentation when help signal is received
        """
        webbrowser.open("/usr/share/hermes/doc/html/index.html")


    def __set_logfile(self):
        """ 
        [es] Metodo privado que crea el fichero de registro
        -------------------------------------------------------------------
        [en] Private method to create the log file
        """
        self.logfilepath = tempfile.mktemp()

        self.logfile = open(self.logfilepath, 'w')
        sys.stdout = self.logfile
