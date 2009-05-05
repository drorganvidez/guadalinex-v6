# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo notification -
# [en] notification module -
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
import thread
import logging
import os
import time

if getattr(dbus, "version", (0, 0, 0)) >= (0, 41, 0):
    import dbus.glib


class NotificationDaemon(object):
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """
    """
    This class is a wrapper for notification-daemon program.
    """

    def __init__(self):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.logger = logging.getLogger()
        bus = dbus.SessionBus()
        obj = bus.get_object('org.freedesktop.Notifications',
                '/org/freedesktop/Notifications')

        self.iface = dbus.Interface(obj, 'org.freedesktop.Notifications')

    # Main Message #######################################################

    def show(self, summary, message, icon, actions = {}): 
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        if actions != {}:
            timeout = 12000
            (notify_actions,action_handlers) = self.__process_actions(actions)
            
            def action_invoked(nid, action_id):
                if action_handlers.has_key(action_id) and res == nid:
                    #Execute the action handler
                    thread.start_new_thread(action_handlers[action_id], ())

                self.iface.CloseNotification(dbus.UInt32(nid))

            condition = False
            while not condition:
                try:
                    self.logger.debug("Trying to connect to ActionInvoked")
                    self.iface.connect_to_signal("ActionInvoked", action_invoked)
                    condition = True
                except:
                    logmsg = "ActionInvoked handler not configured. "
                    logmsg += "Trying to run notification-daemon."
                    self.logger.warning(logmsg)
                    os.system('/usr/lib/notification-daemon/notification-daemon &')                
                    time.sleep(0.2)

        else:
            timeout = 7000
            #Fixing no actions messages
            notify_actions = []

        res = self.iface.Notify("Hermes", 
        dbus.UInt32(0),
                dbus.String(icon),
                summary, 
                message, 
                notify_actions,
        {},
                dbus.UInt32(timeout))
        return res


    # Specific messages #################################

    def show_info(self, summary, message, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        return self.show(summary, message, "gtk-dialog-info", actions)


    def show_warning(self, summary, message, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        return self.show(summary, message, "gtk-dialog-warning", actions)


    def show_error(self, summary, message, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        return self.show(summary, message, "gtk-dialog-error", actions)


    def close(self, nid):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        try:
            self.iface.CloseNotification(dbus.UInt32(nid))
        except:
            pass

# Private methods ###################################
    def __process_actions(self, actions):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        """
        Devuelve una 2-tupla

        La primera es una lista cuyos valores pares (comenzando por 0)
    se refieren a la identificación de la acción y cuyos valores
    impares serán la cadena a mostrar en el botón de la acción

        El segundo contiene como claves los identificadores (enteros) de las
        acciones a tomar y como valores las funciones a ejecutar
        """
        if actions == {}:
            #FIXME
            return {}, {}

        notify_actions = []
        action_handlers = {}
        i = 0
        for key, value in actions.items():
            notify_actions.append(dbus.String(i))
            notify_actions.append(key)
            action_handlers[dbus.String(i)] = value
            i += 1

        return notify_actions, action_handlers

class FileNotification(object):
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """

    def __init__(self, filepath):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.filepath = filepath


    def show (self, summary, body, icon, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.__write("show: %s, %s, %s" % (summary, body, icon))


    def show_info(self, summary, body, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.__write("show_info: %s, %s, %s" % (summary, body))


    def show_warning(self, summary, body, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.__write("show_warning: %s, %s, %s" % (summary, body))


    def show_error(self, summary, body, actions = {}):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        self.__write("show_error: %s, %s, %s" % (summary, body))


    def __write(self, text):
        """ 
        [es] 
        -------------------------------------------------------------------
        [en] 
        """
        try:
            objfile = open(self.filepath, 'a')
            objfile.write(text + '\n')
            objfile.close()
        except Exception, e:
            logging.getLogger().error('FileNotification: ' + e)
