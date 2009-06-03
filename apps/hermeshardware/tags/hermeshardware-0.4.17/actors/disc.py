# -*- coding: utf-8 -*-
#
# Authors: 
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo disc - Módulo que implementa el "actor hardware" para los
#                    discos ROM (CDROM, DVDROM, etc)
# [en] disc module - "Hardware actor" module implementation for ROM discs
#                    (CDROM, DVDROM, etc)
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


import glob
import os.path

from deviceactor import DeviceActor
from gettext import gettext as _


class Actor (DeviceActor):
    """ 
    [es] Implementacion de clase Actor para discos (hereda del actor para 
         volumenes)
    --------------------------------------------------------------------------
    [en] Actor class implementation for disks (uses volume actor as 
         base class)
    """

    __required__ = {'info.category': 'volume', 'volume.is_disc': 1 }
    __icon_path__  = os.path.abspath('actors/img/disc.png') # añadir icono de disco
    __iconoff_path__ = os.path.abspath('actors/img/discoff.png')
    __device_title__ = _("Disc")
    __device_conn_description__ = _("Disc inserted")
    __device_disconn_description__ = _("Disc ejected")
    __filesystem_mounted__ = _("Filesystem mounted")
    __filesystem_umounted__ = _("Filesystem umounted")    
    __listener_factories__ = []

    def on_modified(self, key):
        """
        [es] Acciones a ejecutar cuando se detecta un cambio en el estado
        -----------------------------------------------------------------------
        [en] Actions to take when a status change is detected
        """ 
        if key == 'volume.is_mounted':
            try:
                if self.properties['volume.is_mounted']:
                    mount_point = self.properties['volume.mount_point']

                    def open_volume():
                        os.system('nautilus "%s"' % mount_point) 

                    self.msg_render.show(self.__device_title__,
                         self.__filesystem_mounted__,
                         self.__icon_path__,
                         actions = {mount_point: open_volume})

                    for listener in self.listeners:
                        if listener.is_valid(self.properties):
                            listener.volume_mounted(mount_point)

                else:
                    self.msg_render.show(self.__device_title__,
                            self.__filesystem_umounted__, self.__iconoff_path__) 

                    for listener in self.listeners:
                        if listener.is_valid(self.properties):
                            listener.volume_unmounted()

            except Exception, e:
                self.logger.error(_("Error") + ": " + str(e))

