# -*- coding: utf-8 -*-
#
# Authors:
#     Gumersindo Coronel Pérez (gcoronel)
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo cdrommount - Módulo que implementa el "actor hardware" para
#         solucionar un problema de montaje de algunos CDROMs y DVDROMs en
#         Guadalinex v4.1
# [en] Cdrommount module - implements "hardware actor" to fix mount
#         problems for some CDROM and DVDROM devices with Guadalinex v4.1
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


import os
import gconf

from volume import Actor as VolumeActor

class Actor (VolumeActor):
    """
    [es] Implementación de la clase Actor para montar CDROM y DVDROM
    ---------------------------------------------------------------------------
    [en] CDROM & DVDROM mount Actor class implementation
    """
    __required__ = {
            'volume.is_disc': True,
            'block.is_volume': True
            }

    def on_added(self):
        """
        [es] Cuando se detecta la inserción de un CDROM o un DVDROM se 
             comprueba si está habilitada la opcion de automontaje de
             volumenes. Si es así se procede a montar el dispositivo en la ruta
             de disco definida en fstab.
        -----------------------------------------------------------------------
        [en] When a new CDROM or DVDROM insertion is detected we need to check
             automount_media gnome desktop option. If its value is True we
             proceed to mount the device into the harddisk path defined at
             fstab.
        """
        self.logger.debug("storage.on_add actived")
        client = gconf.client_get_default()
        is_automount = client.get_bool("/desktop/gnome/volume_manager/automount_media")
        self.logger.debug("gconf.key automount_media value is: %s", is_automount)
        if is_automount:
            self.logger.debug("gconf.key automount_media True")
            os.system("pmount %s %s" % (self.properties['block.device',
                 self.properties['linux.fstab.mountpoint'].split('/')[-1]))

            super(VolumeActor, self).on_added()


    def on_removed(self):
        self.logger.debug("storage.on_removed actived")
        os.system("pumount %s" % self.properties['block.device'])

        super(VolumeActor, self).on_removed()
