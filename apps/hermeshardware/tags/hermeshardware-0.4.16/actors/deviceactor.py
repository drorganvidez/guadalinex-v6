# -*- coding: utf-8 -*-
#
# Authors:
#     Gumersindo Coronel Pérez (gcoronel)
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo deviceactor - Contiene la clase DeviceActor, clase base para
#                           la creación de "actores de hardware"
# [en] deviceactor module - Contains DeviceActor class, used for the 
#                           "hardware actors" creation.
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


"""
¿Cómo crear un Actor?

1) Creamos dentro del directorio actors un fichero .py, por ejemplo:
    actors/tvactor.py

2) Dentro de este fichero, lo primero que hacemos es importar la clase
DeviceActor dentro del módulo deviceactors:
        
   from deviceactor import DeviceActor

3) Creamos una clase que ha de llamarse Actor, y que hereda de DeviceActor:

    class Actor (DeviceActor):

4) Indicamos, a través del atributo de clase __required__ (de tipo dict), el nombre
y el valor de las propiedades requeridas para que el actor se active:

    __require__ = {'info.category' : 'tv'}


5) Redefinimos los métodos "on_added", "on_removed" y on_modified, con las acciones que se
deben realiza cuando se añada un dispositivo, se retire o se modifique una
propiedad del dispositivo para el que estamos actuando, respectivamente

Dentro de cualquier clase Actor disponemos de dos atributos sumamente útiles:

    self.msg_render: Es un objeto que implementa la interfaz
    org.guadalinex.TrayInterface, el cual usamos para comunicarnos con el
    usuario

    self.properties: Es un diccionario que contiene todas las propiedades del
    dispositivo sobre el que estamos actuando, proporcionado por HAL


El ejemplo completo:

------ actors/tvactor.py ------

from deviceactor import DeviceActor

class Actor(DeviceActor):
    __required__ ={'info.category': 'tv'}

    def on_added(self):
        self.msg_render.show_info("Dispositivo de tv detectado")

    def on_removed(self):
        self.msg_render.show_info("Dispositivo de tv desconectado")

    

"""

import os
import logging

import dbus
import yaml

from utils.pkginstaller import PkgInstaller
from gettext import gettext as _

class DeviceActor(object):
    """ 
    [es] Esta clase encapsula la lógica de actuación ante eventos en un 
         dispositivo. Es una clase abstracta que sirve para crear 
         "actores de dispositivos", que sirven para mostrar mensajes al 
         insertar/quitar dispositivos
    ---------------------------------------------------------------------------
    [en] This class encapsulates the device related events handling logic.
         It is an abstract class to create "device actors" to notify the user
         about events related to those hardware devices.
    """

    __required__ = {}
    # [es] Valores: 1, 2, 3, 4, 5. A mayor valor, mayor prioridad.
    # [en] Values: 1, 2, 3, 4, 5. The higher value, the more priority.
    __priority__ = 3 

    # [es] Propiedades necesarias para la notificacion. Se deben definir
    #      en cada actor. Por defecto en blanco.
    # [en] Notification needed properties. To be defined by each actor·
    #      Blank by default.
    __icon_path__  = ''
    __iconoff_path__ = ''
    __device_title__ = ''
    __device_conn_description__ = ''
    __device_disconn_description__ = ''

    # [es] Puede ser usado por un actor para deshabilitar otro actor.
    # [en] This can be used by an actor to disable another actor.
    __enabled__ = True 


    def __init__(self, message_render, device_properties):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """
        self.message_render = self.msg_render = message_render
        self.properties = device_properties
        self.msg_no = None
        self.udi = device_properties['info.udi']
        self.logger = logging.getLogger()


    def __on_property_modified(self, udi, num, values):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """
        for ele in values:
            key = ele[0]

            # [es] Actualizamos las propiedades
            # [en] Update properties
            obj = self.bus.get_object('org.freedesktop.Hal', self.udi)
            obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')
            self.properties = obj.GetAllProperties()

            self.on_modified(key)

    def on_added(self):
        """ 
        [es] Interfaz para las acciones a ejecutar cuando se conecta el
             dispositivo
        -----------------------------------------------------------------------
        [en] Interface for the actions to take when the device is connected
        """
        self.msg_render.show(self.__device_title__, 
                             self.__device_conn_description__,
                             self.__icon_path__)

    def on_removed(self):
        """ 
        [es] Interfaz para las acciones a ejecutar cuando se desconecta el
             dispositivo
        -----------------------------------------------------------------------
        [en] Interface for the actions to take when the device is disconnected
        """
        self.msg_render.show(self.__device_title__,
                             self.__device_disconn_description__,
                             self.__iconoff_path__)
    
    def on_modified(self, prop_name):
        """ 
        [es] Interfaz para las acciones a ejecutar cuando se modifica alguna el
             propiedad del dispositivo
        -----------------------------------------------------------------------
        [en] Interface for the actions to take when the device property is 
             modified
        """
        pass


class PkgDeviceActor(DeviceActor):
    """ 
    [es] Esta clase encapsula la lógica para los actores que necesitan
         comprobar e instalar paquetes determinados.
         Es útil para simplicar todo esos actores que lo único que hacen es
         instalar software para que el dispositivo funcione.
    ---------------------------------------------------------------------------
    [en] This class encapsulates required logic for actors that need to check
         and install packages.
         Intends to simplify all those actors that need installing software in
         order to make the device work.
    """
	
    #__icon_path__  = ''
    #__iconoff_path__ = ''
    #__device_title__ = ''
    #__device_conn_description__ = ''
    #__device_disconn_description__ = ''
    __device_use_title__ = _('Use device')

    __packages__ = []

    __conn_commands__ = []
    __disconn_commands__ = []


    def __init__(self, message_render, device_properties):
        """ 
        [es] Metodo de inicializacion
        -----------------------------------------------------------------------
        [en] Initialization method
        """
        DeviceActor.__init__(self, message_render, device_properties)
        self.set_default_properties()


    def set_default_properties(self):
        """
        [es] Establece las propiedades por defecto desde los ficheros de 
             configuracion
        -----------------------------------------------------------------------
        [en] Set default properties from config files.
        """
        modname = self.__module__.split('.')[-1]
        config = None
        pkg_path = os.path.abspath('actors/config') + \
                '/' + modname + '.' + PkgDeviceActor._get_desktop()
        try:
            config = yaml.load(open(pkg_path).read())
        except Exception, e:
            print e

        if config:
            if not self.__packages__:
                self.__packages__ = config.get('packages', [])
            if not self.__conn_commands__:
                self.__conn_commands__ = config.get('conn_commands', [])
            if not self.__disconn_commands__:
                self.__disconn_commands__ = config.get('disconn_commands', [])


    def get_packages(module_name):
        """ 
        [es] Devuelve los paquetes para un actor en funcion de actors/config/*
             y de la configuración del entorno de usuario.
        -----------------------------------------------------------------------
        [en] Returns packages for an actor based on actors/config/* files and 
             on user's desktop.
        """
        pkg_path = os.path.abspath('actors/config') + \
                '/' + module_name + '.' + PkgDeviceActor._get_desktop()
        config = {}
        try:
            config = yaml.load(open(pkg_path).read())
        except Exception, e:
            pass

        return config.get('packages', [])

    get_packages = staticmethod(get_packages)


    def _get_desktop():
        """ 
        [es] Devuelve el nombre del escritorio (gnome o kde)
        -----------------------------------------------------------------------
        [en] Return desktop name (gnome, or kde)
        """
        # [es] Buscamos el proceso gnome
        # [en] Look for gnome process
        gnome_command = 'ps ux|grep gnome-settings|grep -v grep'
        is_gnome = bool(os.popen(gnome_command).read())
        if is_gnome:
            return "gnome"

        # [es] Buscamos el proceso kde
        # [en] Look for kde process
        kde_command = 'ps ux|grep startkde|grep -v grep'
        is_kde = bool(os.popen(kde_command).read())
        if is_kde:
            return "kde"
        # [es] Por defecto consideramos gnome
        # [en] We consider gnome, by default 
        return "gnome"

    _get_desktop = staticmethod(_get_desktop)


    def on_added(self):
        """
        [es] Se lanza cuando se detecta la conexion de un dispositivo que
             que requiere algun software instalado.
        -----------------------------------------------------------------------
        [en] Runs when a device that needs some software installation is 
             detected.
        """
        s = PkgInstaller()

        def execute_conn_commands():
            """ 
            [es] Ejecuta los comandos necesarios para conectar el dispositivo
            -------------------------------------------------------------------
            [en] Runs the needed commands when the device is connected
            """
            execute = True

            # [es] Obtiene permisos mediante sudo si es necesario instalar algo
            # [en] Obtain sudo permission if needed to install something
            for command in self.__conn_commands__:
                if command.strip().startswith('sudo'):
                    if not get_sudo():
                        execute = False
                    break

            if execute:
                for command in self.__conn_commands__:
                    os.system(command)

        def install_packages():
            """ 
            [es] Ejecuta la instalacion de los paquetes en __packages__
            -------------------------------------------------------------------
            [en] Installs packages from __packages__
            """
            s.install(self.__packages__)
            execute_conn_commands()

        if s.check(self.__packages__):
            if self.__conn_commands__:
                actions = {self.__device_use_title__: execute_conn_commands}
            else:
                actions = {}
        else:
            actions = {_("Install required packages"): install_packages}

        self.msg_render.show(self.__device_title__, 
                             self.__device_conn_description__,
                             self.__icon_path__, actions = actions)


    def on_removed(self):
        """ 
        [es] Acciones a tomar cuando se detecta la desconexion del dispositivo
        -----------------------------------------------------------------------
        [en] Actions to execute when device disconnection is detected
        """
        self.msg_render.show(self.__device_title__,
                self.__device_disconn_description__,
                self.__iconoff_path__)
        self._execute_disconn_commands()


    def _install_packages(self):
        """ 
        [es] Instala todos los paquetes en __packages__
        -----------------------------------------------------------------------
        [en] Installs all the packages in __packages__
        """
        s = PkgInstaller()
        s.install(self.__packages__)


    def _execute_conn_commands(self):
        """ 
        [es] Ejecuta los comandos de conexion en __conn_commands__
        -----------------------------------------------------------------------
        [en] Executes all the connection commands in __conn_commands__
        """
        for command in self.__conn_commands__:
            os.system(command)


    def _execute_disconn_commands(self):
        """
        [es] Ejecuta los comandos de desconexion en __disconn_commands__
        -----------------------------------------------------------------------
        [en] Executes all the disconnection commands in __disconn_commands__
        """
        for command in self.__disconn_commands__:
            os.system(command)

