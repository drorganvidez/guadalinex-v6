# -*- coding: utf8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo devicelist - Permite mantener la lista de dispositivos 
#      conectados 
# [en] devicelist module - Maintains the conected devices list
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

import dbus
import pickle
import logging
import os
import pwd
import time

from gettext import gettext as _
from sets import Set

class DeviceList:
    """ 
    [es] Esta clase implementa toda la lógica necesaria para comprobar si
         se han añadido/quitado dispositivos "en frio"
    -----------------------------------------------------------------------
    [en] This class implements all the logic needed to check if any device 
         has been added/removed coldly
    """


    # [es] Fichero por defecto que se usara para almacenar la lista de 
    #      dispositivos
    # [en] Default file tobe used to store the device list
 
    DEFAULT_FILE = '/var/tmp/devicelist-file-' + os.environ['USER'] + \
                   str(os.getuid())

    def __init__(self):
        """ 
        [es] inicializamos la lista de dispositivos con los encontrados en
             el sistema
        -------------------------------------------------------------------
        [en] initialize device list with the ones found attached
        """
        self.logger = logging.getLogger()
        self.__udi_set = Set()
        self.__properties_dict = {}
        self.__data = (self.__udi_set, self.__properties_dict)
        self.__data_to_compare = None

        self.__setup()
        self.set_file_to_compare()


    def save(self, filename = DEFAULT_FILE):
        """ 
        [es] Guardamos la lista en un fichero. Por defecto en DEFAULT_FILE
        -------------------------------------------------------------------
        [en] Save the list to a file. By default we use DEFAULT_FILE
        """
        try:
            file = open(filename, 'w')
            pickle.dump(self.__data, file)
            file.close()
        except Exception, e:
            self.logger.error(str(e))


    def set_file_to_compare(self, filename = DEFAULT_FILE):
        """ 
        [es] Comunica a DeviceList que use ese fichero para comparar los 
             dispositivos
        -------------------------------------------------------------------
        [en] Comunicates DeviceList to use this file for comparing devices
        """
        try:
            file = open(filename, 'r')
        except IOError:
            self.logger.warning(_("Creating ") + filename)
            self.save(filename)
            file = open(filename, 'r')

        try:
            self.__data_to_compare = pickle.load(file)
            file.close()
        except EOFError, e:
            self.__data_to_compare = {0:Set([])}
            self.logger.warning(_("Error reading from: ") + filename)



    def get_added(self):
        """ 
        [es] Devuelve una lista de tuplas (udi, properties) que contiene la
             informacion sobre dispositivos conectados.
        -------------------------------------------------------------------
        [en] Returns a list of tuples (udi,properties) containing the 
             added devices data.
        """
        system_udis = self.__data[0]
        store_udis = self.__data_to_compare[0]

        udis_added = system_udis - store_udis

        res = []
        for udi in udis_added:
            res.append((udi, self.__data[1][udi]))

        return res


    def get_removed(self):
        """ 
        [es] Devuelve una lista de tuplas (udi, properties) que contiene la
             informacion sobre dispositivos desconectados.
        -------------------------------------------------------------------
        [en] Returns a list of tuples (udi,properties) containing the 
             removed devices data.
        """
        system_udis = self.__data[0]
        store_udis = self.__data_to_compare[0]

        udis_removed = store_udis - system_udis 

        res = []
        for udi in udis_removed:
            res.append((udi, self.__data_to_compare[1][udi]))

        return res


    def __setup(self):
        """ 
        [es] Para cada dispositivo presente en el sistema carga en el
             objeto DeviceList todos los UDI y las correspondientes
             propiedades en self.__udi_set() y en self.__properties_dict[]
        -------------------------------------------------------------------
        [en] For each device conected to the systemloads inthe DeviceList 
             object all the UDI and corresponding properties in 
             self.__udi_set() and self.__properties_dict[]
        """
        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
        manager = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')

        for udi in manager.GetAllDevices():
            devobj = bus.get_object('org.freedesktop.Hal', udi)
            devobj = dbus.Interface(devobj, 'org.freedesktop.Hal.Device')

            self.__udi_set.add(udi)
            self.__properties_dict[udi] = devobj.GetAllProperties()


