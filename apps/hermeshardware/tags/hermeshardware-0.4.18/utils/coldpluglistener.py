# -*- coding: utf8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo coldpluglistener - 
# [en] coldpluglistener module - 
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


import thread
import time
import logging

from gettext import gettext as _ 

from utils import DeviceList

class ColdPlugListener:
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """

    def __init__(self, devicelistener):
        """ 
        [es] Método de inicializacion
        -------------------------------------------------------------------
        [en] Initialization method
        """
        self.devicelistener = devicelistener
        self.thread = None
        self.logger = logging.getLogger()
        
    def start(self):
        """ 
        [es] Método público que arranca el proceso de escucha
        -------------------------------------------------------------------
        [en] Listen process starting public method
        """
        self.thread = thread.start_new_thread(self.__run, ())
        self.logger.debug(_("Starting coldplug thread"))

    def __run(self):
        """ 
        [es] Método privado que inicia la ejecución
        -------------------------------------------------------------------
        [en] Exec starting private method
        """
        self.logger.info(_("ColdPlugListener thread started"))
        
        # [es] Obtenemos la lista de dispositivos conectados al sistema
        # [en] We get a list we all the attached devices 
        dl = DeviceList()

        for ele in dl.get_added():
            try:
                self.logger.debug(_("Coldplug: DeviceAdded: ") + str(ele[0]))

                # [es] ele[0] contiene el UDI del dispositivo
                # [en] ele[0] contains the device UDI
                self.devicelistener.on_device_added(ele[0]) 
                time.sleep(0.5)
            except Exception, e:
                self.logger.warning(str(e))

        for ele in dl.get_removed():
            try:
                udi = ele[0]
                properties = ele[1]
                self.devicelistener.get_actor_from_properties(properties)
                self.logger.debug(_("Coldplug: DeviceRemoved: ") + str(udi))
                self.devicelistener.on_device_removed(udi)
                time.sleep(0.5)
            except Exception, e:
                self.logger.warning(str(e))

        dl.save()
