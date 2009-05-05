# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo grepmap - Identifica modulos del kernel para un dispositivo 
# [en] grepmap module - Identifies kernel modules for a given device
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

class UsbGrepMap(object):
    """ 
    [es] Identifica modulos del kernel para un dispositivo  
    -----------------------------------------------------------------------
    [en] Identifies kernel modules for a given device
    """

    DEFAULTMAPFILE = '/etc/hotplug/usb/libsane.usermap'

    def get_module(self, vendorid, productid, mapfile = DEFAULTMAPFILE):
        """ 
        [es] Devuelve el nombre del modulo para el dispositivo identificado
             por vendorid y productid
             @param vendorid     Identificador de Fabricante en hexadecimal.
             @param productid    Identificador de Producto en hexadecimal.
        --------------------------------------------------------------------
        [en] Returns the module name for device with vendorid and productid
             @param vendorid     Vendor Id in hexadecimal.
             @param productid    Product Id in hexadecimal.
        """

        vendorid = hex(vendorid)
        productid = hex(productid)

        command = "grepmap --usbmap "
        command += "--file=%s %s %s 0 0 0 0 0 0 0" % \
                (mapfile, vendorid, productid)

        return os.popen(command).read().strip()




        


