# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo volume - Módulo que implementa el "actor hardware" para los
#                      dispositivos de volumen (dispositivos que se montan
#                      como unidades de disco)
# [en] volume module - "Hardware actor" module implementation for volume
#                      devices (devices mounted like disk mounts)
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

#VOLUMEICON = os.path.abspath('actors/img/volume.png') 

class Actor (DeviceActor):
    """ 
    [es] Implementacion de clase Actor para volumenes(sistemas de ficheros)
    --------------------------------------------------------------------------
    [en] Actor class implementation for volume devices (filesystems)
    """

    __required__ = {'info.category': 'volume'}
    __icon_path__  = os.path.abspath('actors/img/volume.png')
    __iconoff_path__ = os.path.abspath('actors/img/volumeoff.png')
    __device_title__ = _("Storage")
    __device_conn_description__ = _("Volume mounted")
    __device_disconn_description__ = _("Volume umounted")
    __listener_factories__ = []

    def __init__(self, *args, **kwargs):
        """
        [es] Clase de inicializacion del actor
        -----------------------------------------------------------------------
        [en] Actor initialization class
        """ 
        super(Actor, self).__init__(*args, **kwargs)

        self.listeners = [factory() for factory in self.__listener_factories__]

    def register_listener(cls, listener):
        """
        [es] Registramos el monitor
        -----------------------------------------------------------------------
        [en] Listener registration
        """ 
        cls.__listener_factories__.append(listener)

    register_listener = classmethod(register_listener)

    #def on_added(self):
    #    self.msg_render.show_info("Dispositivo de volumen conectado")

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

                    self.message_render.show(_("Storage"), 
                        __device_conn_description__, __icon_path__,
                        actions = {mount_point: open_volume})

                    for listener in self.listeners:
                        if listener.is_valid(self.properties):
                            listener.volume_mounted(mount_point)

                else:
                    self.message_render.show(_("Storage"),
                            __device_disconn_description__, __iconoff_path__) 

                    for listener in self.listeners:
                        if listener.is_valid(self.properties):
                            listener.volume_unmounted()

            except Exception, e:
                self.logger.error(_("Error") + ": " + str(e))

class AutoRegister(type):
    """ 
    [es] Esta meta clase registra automáticamente cada clase como un
         monitor de Actor
    -----------------------------------------------------------------------
    [en] This meta class auto register each class as an Actor listener
    """
    def __new__(mcs, name, bases, dic):
        t = type.__new__(mcs, name, bases, dic)
        if name != 'VolumeListener': # don't register the abstract base class
            Actor.register_listener(t)
        return t

class VolumeListener(object):
    """ 
    [es] Un monitor de volumenes es un proceso que lanza notificaciones
         cuando detecta algún cambio en el estado de un volumen
    -----------------------------------------------------------------------
    [en] A Volume Listener launches notifications when the state of a
         volume changes
    """

    __metaclass__ = AutoRegister

    def is_valid(self, properties):
        """
        [es] Este metodo actua como un filtro. En base a las propiedades de 
             HAL para el dispositivo, este método devuelve:
                - True si el monitor debe ser usado
                - False en cualquier otro caso
        -----------------------------------------------------------------------
        [en] This method acts like a filter.
             Based on the HAL properties this method should returns
                - True if this listener should be used
                - False otherwise
        """
        return False

    def volume_mounted(self, mount_point):
        """
        [es] Acciones a tomar cuando el volumen se monta
        -----------------------------------------------------------------------
        [en] This is called when the volume is mounted
        """ 

    def volume_unmounted(self):
        """
        [es] Acciones a tomar cuando el volumen se desmonta
        -----------------------------------------------------------------------
        [en] This is called when the volume is unmounted 
        """

CERTMANAGER_CMD = '/usr/bin/certmanager.py'

class CertificateListener(VolumeListener):
    """ 
    [es] Invocamos a cert_manager para detectar si el volumen contiene
         ceritificados electronicos y para configurar a las aplicaciones
         correspondientes para que los puedan usar. Sólo valido para 
         discos USB
    -----------------------------------------------------------------------
    [en] Call cert_manager to detect certificates in the volume and to
         setup the main applications to use them
         Only valid for USB storage disks.
    """
    def __init__(self):
        """ 
        [es] Clase de inicializacion
        -------------------------------------------------------------------
        [en] Initialization class
        """
        super(CertificateListener, self).__init__()
        self.mount_point = None

    def is_valid(self, properties):
        """ 
        [es] Verificamos si se cumplen determinadas propiedades para lanzar
             el monitor
        -------------------------------------------------------------------
        [en] We check wether some properties exist to launch the listener
        """
        if properties.get('volume.mount_point', None):
            if glob.glob(properties.get('volume.mount_point', None)+'/*.p12'):
                return True
        return False

    def volume_mounted(self, mount_point):
        """
        [es] Acciones a ejecutar cuando se monta el volumen
        -------------------------------------------------------------------
        [en] Actions to take when the volume gets mounted
        """
        self.mount_point = mount_point

        if os.path.exists(CERTMANAGER_CMD):
            os.system('%s -p "%s"' % (CERTMANAGER_CMD, self.mount_point))

    def volume_unmounted(self):
        """ 
        [es] Acciones a ejecutar cuando se desmonta el volumen
        -------------------------------------------------------------------
        [en] Actions to take when the volume gets unmounted
        """
        if os.path.exists(CERTMANAGER_CMD):
            user_dir = os.path.expanduser('~')
            log_file = os.path.join(user_dir, '.certmanager.log')
            if os.path.exists(log_file):
                os.system('%s -u %s' % (CERTMANAGER_CMD, log_file))
        self.mount_point = None
