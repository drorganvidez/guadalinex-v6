# -*- coding: utf-8 -*-
#
# Authors:
#     Gumersindo Coronel Pérez (gcoronel)
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo dvbfw - Módulo que implementa el "actor hardware" para los
#                     sintonizadores de TDT con problemas de firmware
# [en] dvbfw module - Implements hardware actor for DVB devices with no
#                     firmware files
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
import webbrowser

from gettext import gettext as _

from dvb import Actor as DvbActor

def get_usbmap():
    valid_list = ['cinergyT2', 'b2c2', 'bt8xx', 'ttusb-budget', 
                  'pluto2', 'ttpci', 'ttusb-dec'] 

    kernel_version = os.popen('uname -r').read().strip()
    try:
        usbmap_file = open('/lib/modules/%s/modules.usbmap' % kernel_version)
    except IOError:
        return []

    result = []
    for line in usbmap_file.readlines():
        line = line.strip()
        if line.startswith('#'):
            continue
        raw_c = line.split()
        components = (raw_c[0], raw_c[2], raw_c[3])

        if (components[0] in valid_list) or\
                components[0].startswith('dvb-usb'):
            result.append(components)

    return result


def is_valid_vendor(value):
    i = 0
    value = int(value)
    global vendor_id
    vendor_id = None
    for vid in Actor.usbmap:
        if value == eval(vid[1]):
            vendor_id = value
            return True
        i += 1
    return False


def is_valid_product(value):
    if vendor_id:
        product_id = int(value)
        vplist = [(eval(ele[1]), eval(ele[2])) for ele in Actor.usbmap]
        return (vendor_id, product_id) in vplist



class Actor(DvbActor):
    """ 
    [es] Dispositivos DVB (Sintonizadores de TDT) que no disponen
         de firmware
    --------------------------------------------------------------
    [en] DVB devices which haven't got firmware files.
    """

    usbmap = get_usbmap()

    __required__ = {'info.subsystem': 'usb',
                    'usb.vendor_id': is_valid_vendor,
                    'usb.product_id': is_valid_product,}

    # [es] Importante para compatibilidad con actor dvb
    # [en] Important for compatibility with dvb actor
    __priority__ = 3

    def on_added(self):
        """
        [es] Acciones a ejecutar cuando se conecta el dispositivo
        -------------------------------------------------------------------
        [en] Actions to take when the device gets connected
        """
        def open_browser():
            webbrowser.open('http://www.guadalinex.org/distro/V6/hermes/tdt')

        self.msg_render.show_warning(__device_title__, 
                                     _('DVB device without firmware!!'),
                                     actions = {_('More info...'): open_browser})
