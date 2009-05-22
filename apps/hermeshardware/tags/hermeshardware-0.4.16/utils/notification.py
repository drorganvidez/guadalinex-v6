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

from gettext import gettext as _

if getattr(dbus, "version", (0, 0, 0)) >= (0, 41, 0):
    import dbus.glib

class NotificationDaemon(object):
    """ 
    [es] Esta clase es una implementacion del demonio de notificaciones 
         (notification-daemon)
    -----------------------------------------------------------------------
    [en] This class is a wrapper for notification-daemon program.
    """

    def __init__(self):
        """ 
        [es] Método de inicializacion
        -------------------------------------------------------------------
        [en] Intialization method
        """
        self.logger = logging.getLogger()
        bus = dbus.SessionBus()
        obj = bus.get_object('org.freedesktop.Notifications',
                '/org/freedesktop/Notifications')

        self.iface = dbus.Interface(obj, 'org.freedesktop.Notifications')

    # [es] Mensaje principal
    # [en] Main Message 

    def show(self, summary, message, icon, actions = {}): 
        """ 
        [es] Metodo para mostrar una informacion emergente en el area de 
             usuario
        -------------------------------------------------------------------
        [en] Method to show up information on the user Desktop
        """
        if actions != {}:
            timeout = 12000
            (notify_actions,action_handlers) = self.__process_actions(actions)

            def action_invoked(nid, action_id):
                if action_handlers.has_key(action_id) and res == nid:
                    # [es] Se ejecuta el manejador de acciones
                    # [en] Execute the action handler
                    thread.start_new_thread(action_handlers[action_id], ())

                self.iface.CloseNotification(dbus.UInt32(nid))

            condition = False
            while not condition:
                try:
                    self.logger.debug(_("Trying to connect to ActionInvoked"))
                    self.iface.connect_to_signal("ActionInvoked", action_invoked)
                    condition = True
                except:
                    logmsg = _("ActionInvoked handler not configured.")
                    logmsg += _("Trying to run notification-daemon.")
                    self.logger.warning(logmsg)
                    os.system('/usr/lib/notification-daemon/notification-daemon &')
                    time.sleep(0.2)

        else:
            timeout = 7000
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

    # [es] Mensajes específicos
    # [en] Specific messages 

    def show_info(self, summary, message, actions = {}):
        """ 
        [es] Metodo para mostrar notificacion informativa, incluimos icono 
             de informacion de gtk por defecto
        -------------------------------------------------------------------
        [en] Method to show up an informative notification, we include the 
             default information gtk icon
        """
        return self.show(summary, message, "gtk-dialog-info", actions)


    def show_warning(self, summary, message, actions = {}):
        """ 
        [es] Metodo para mostrar notificacion de advertencia, incluimos 
             icono de alerta de gtk por defecto
        -------------------------------------------------------------------
        [en] Method to show up a warning notification, we include the 
             default warning gtk icon
        """
        return self.show(summary, message, "gtk-dialog-warning", actions)


    def show_error(self, summary, message, actions = {}):
        """ 
        [es] Metodo para mostrar notificacion de error, incluimos icono 
             de error de gtk por defecto
        -------------------------------------------------------------------
        [en] Method to show up an error notification, we include the 
             default error gtk icon
        """
        return self.show(summary, message, "gtk-dialog-error", actions)


    def close(self, nid):
        """ 
        [es] Método para cerrar la ventana  de notificación 
        -------------------------------------------------------------------
        [en] Method to close the notification window
        """
        try:
            self.iface.CloseNotification(dbus.UInt32(nid))
        except:
            pass
    
    # [es] Métodos privados
    # [en] Private methods 
    def __process_actions(self, actions):
        """ 
        [es] Devuelve una tupla:

             El primer elemento es una lista cuyos valores pares (comenzando 
             por 0) se refieren a la identificación de la acción y cuyos 
             valores impares serán la cadena a mostrar en el botón de la 
             acción

             El segundo contiene como claves los identificadores (enteros) 
             de las acciones a tomar y como valores las funciones a ejecutar
        --------------------------------------------------------------------
        [en] Returns a tuple:

             First element is a list. Odd position values (starting at 0)
             refer to the action identifiers and even position values are
             strings to show on the action button.

             Second contains, as keys, actions to take identificators 
             (integers), and as its values functions to execute.
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
    [es] Clase para escribir notificaciones a fichero
    -----------------------------------------------------------------------
    [en] Class to save notifications to file
    """

    def __init__(self, filepath):
        """ 
        [es] Método de inicializacion. Identificamos el fichero en el que 
             vamos a escribir.
        -------------------------------------------------------------------
        [en] Initialization method. We identify the file to write in.
        """
        self.filepath = filepath


    def show (self, summary, body, icon, actions = {}):
        """ 
        [es] Método para escribir a fichero una notificacion
        -------------------------------------------------------------------
        [en] Method to save to a file a notification
        """
        self.__write(_("show:") + " %s, %s, %s" % (summary, body, icon))


    def show_info(self, summary, body, actions = {}):
        """ 
        [es] Método para escribir a fichero una notificacion
        -------------------------------------------------------------------
        [en] Method to save to a file a notification
        """
        self.__write(_("show_info:") + " %s, %s, %s" % (summary, body))


    def show_warning(self, summary, body, actions = {}):
        """ 
        [es] Método para escribir a fichero una notificacion de advertencia
        -------------------------------------------------------------------
        [en] Method to save to a file a warning notification
        """
        self.__write(_("show_warning:") + " %s, %s, %s" % (summary, body))


    def show_error(self, summary, body, actions = {}):
        """ 
        [es] Método para escribir a fichero una notificacion de error
        -------------------------------------------------------------------
        [en] Method to save to a file an error notification
        """
        self.__write(_("show_error:") + " %s, %s, %s" % (summary, body))


    def __write(self, text):
        """ 
        [es] Método privado para escribir a fichero un texto
        -------------------------------------------------------------------
        [en] Private method to write to a file a given text
        """
        try:
            objfile = open(self.filepath, 'a')
            objfile.write(text + '\n')
            objfile.close()
        except Exception, e:
            logging.getLogger().error(_("FileNotification: ") + e)
