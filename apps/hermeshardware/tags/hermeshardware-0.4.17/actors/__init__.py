# -*- coding: utf8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo __init__ - 
# [en] __init__ module -
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

ACTORSLIST = []
CATEGORIES = {}
BUSSES = {}

import os
import os.path
import logging

from gettext import gettext as _

DIR = os.path.dirname(__file__) + os.sep 
file_list = [ele for ele in os.listdir(DIR) if os.path.isfile(DIR + os.sep + ele)]

logger = logging.getLogger()
logger.debug(_("/##################### IMPORTING ACTORS"))
for filename in file_list:

    if filename == '__init__.py' or filename.split('.')[-1] != 'py' or \
            filename  == 'deviceactor.py':
        continue
    
    module_name = filename.split('.')[0]
    try:
        actor_module = __import__(module_name, globals(), locals(),['*']) 
        ACTORSLIST.append(actor_module.Actor)
        logger.debug("\t" + module_name + " ..... OK")

    except Exception, e:
        logger.warning("%s ..... FAILED. %s" % (module_name, e))
logger.debug(_("\##################### ACTORS IMPORTED")) 
