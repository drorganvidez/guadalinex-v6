# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo sudo - Módulo que intenta ganar permiso de sudo
#      para el usuario. 
# [en] sudo module -
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
import logging
from gettext import gettext as _

def get_sudo():
    """ 
    [es] Devuelve VERDADERO si el usuario adquirió permiso de uso de sudo.
         FALSO en caso contrario. El usuario tiene 3 intentos para
         introducir una contraseña válida para sudo.
         Necesario para ejecutar acciones que requieran permisos de 
         administrador como la instalacion de paquetes en el sistema 
    -----------------------------------------------------------------------
    [en] Returns TRUE if user has login as sudoer. False otherwise. Asks
         user for a sudo valid password for 3 times.
         Needed to execute root permission required actions, such as system
         package installation.
    """
    logger = logging.getLogger() 
    #Try for password. Three times.
    res = 768 
    attemps = 0

    # [es] Error num. 768: Contraseña incorrecta
    # [en] Errno 768: Bad password
    while res == 768 and attemps < 3:
        res = os.system('gksudo -m "%s" /bin/true' % _('Type password'))

        # [es] Error num. 512: El usuario presiono CANCEL
        # [en] Errno 512: User pressed CANCEL
        if res == 512:
            logger.debug(_("User pressed cancel"))
            return False
        attemps += 1

    if res == 768:
        logger.debug(_("Three attemps for password"))
        return False

    return True


if __name__ == '__main__':
    get_sudo()
