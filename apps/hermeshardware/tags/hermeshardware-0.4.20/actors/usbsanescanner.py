# -*- coding: utf-8 -*-
#
# Authors:
#     Gumersindo Coronel Pérez (gcoronel)
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo usbsanescanner - Módulo que implementa el "actor hardware" 
#                              para los escaneres USB soportados por SANE
# [en] usbsanescanner module - Implements hardware actor for SANE supported
#                              USB scanners
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
import os.path
import dbus

from deviceactor import DeviceActor
from gettext import gettext as _

def is_valid(value):
    return 'scanner' in value
    

class Actor (DeviceActor):
    """ 
    [es] Implementacion de clase Actor para escaneres USB soportados por SANE
    --------------------------------------------------------------------------
    [en] Actor class implementation for SANE supported USB Scanners
    """

    __required__ = {'info.subsystem':'usb',
                    'scanner.access_method':'proprietary',
                    'info.capabilities': is_valid}
    __icon_path__  = os.path.abspath('actors/img/scanner.png')
    __iconoff_path__ = os.path.abspath('actors/img/scanneroff.png')
    __device_title__ = _("SANE supported Scanner")
    __device_conn_description__ = _("USB SANE Scanner connected")
    __device_disconn_description__ = _("USB SANE Scanner disconnected")


    def on_added(self):
        """
        [es] Acciones a ejecutar cuando se conecta el dispositivo
        -----------------------------------------------------------------------
        [en] Actions to take when the device is connected
        """
        def open_xsane():
            os.system('xsane')
        
        self.msg_render.show(self.__device_title__,
                             self.__device_conn_description__,
                             self.__icon_path__,
                             actions = {_("Launch Scanning Application"): open_xsane})