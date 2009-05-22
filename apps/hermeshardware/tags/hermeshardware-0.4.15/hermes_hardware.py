#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Authors:
#     Gumersindo Coronel Pérez (gcoronel)
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo hermes_hardware - Notificador de cambios en el hardware
# [en] hermes_hardware module - Hardware detected changes notificator
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




def setup_gettext(domain, data_dir):
    """ 
    [es] Configura el subsistema de localización para dar soporte a 
         las traducciones de la aplicación que estén disponibles.
         Selecciona el dominio que se recibe como parámetro.
    ---------------------------------------------------------------------------
    [en] Sets up the localization subsystem to support the different
         translation packages available
         Selects the domain passed as a parameter
    """
    directory = os.path.abspath(os.path.join(data_dir, "locale"))
    gettext.bindtextdomain(domain, directory)
    if hasattr(gettext, 'bind_textdomain_codeset'):
        gettext.bind_textdomain_codeset(domain, 'UTF-8')
    gettext.textdomain(domain)

    locale.bindtextdomain(domain, directory)
    if hasattr(locale, 'bind_textdomain_codeset'):
        locale.bind_textdomain_codeset(domain, 'UTF-8')
    locale.textdomain(domain)

import dbus
if getattr(dbus, "version", (0, 0, 0)) >= (0, 41, 0):
    import dbus.glib
import logging
import gtk
import gtk.gdk
import os
import os.path
import sys
import traceback
import types

# i18n
import gettext, locale
from gettext import gettext as _
import defs
setup_gettext('hermes-hardware', defs.DATA_DIR)

from utils.hermestrayicon import HermesTrayIcon
from utils import DeviceList, ColdPlugListener, CaptureLogGui
from optparse import OptionParser
from utils.notification import NotificationDaemon, FileNotification
import actors


class DeviceListener:
    """
    [es] Esta es la clase principal de Hermes. Desde aqui se monitoriza el
         sistema y cuando se detectan alertas sobre la conexión, desconexón
         o modificación de algún componente hardware del sistema se ejecutan
         las acciones correspondientes, dependiendo del caso.
         Por ejemplo, si se detecta la conexion "en caliente" de un nuevo 
         dispositivo, se lanza un procedimiento de reconocimiento por 
         comparación con la base de hardware reconocido (actores) y si se 
         identifica positivamente el nuevo dispositivo, se ponen en marcha 
         las actuaciones definidas para simplificar la inserción del nuevo 
         hardware en el entorno de usuario.
    ---------------------------------------------------------------------------
    [en] This is Hermes main class. It does the system monitoring so when
         changes on the state of any of the system hardware components are 
         detected, it executes the proer actions, depending on the case. 
         For example, if the connection of a new hardware is detected, it 
         launches an identification process by comparing with the known 
         hardware base (named actors) and if a matching is found it starts the
         proper procedure to simplify the insertion of the hardware in the user
         environment.
    """
    def __init__(self, message_render, with_cold = True):
        """
        [es] Registramos el monitor de cambios en el hardware y lo conectamos
             a las señales del bus que alertan de la conexión o desconexión de
             dispositivos.
             Parametros:
                 message_render: interfaz a la que enviar las notificaciones
                 with_cold: booleano para indicar si se lanza el Monitor
                            de dispositivos conectados en frio
        -----------------------------------------------------------------------
        [en] Register the device listener and attaches it to the corresponding
             bus signals that alert about devices connection or discnnection.
             Params:
                 message_render: interface for sending notifications through
                 with_cold: boolean indicating wether we launch the Cold Plug 
                            Listener
        """
        self.message_render = message_render
        self.logger = logging.getLogger()

        self.bus = dbus.SystemBus()

        obj = self.bus.get_object('org.freedesktop.Hal',
                                  '/org/freedesktop/Hal/Manager')

        self.hal_manager = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')

        self.hal_manager.connect_to_signal('DeviceAdded', self.on_device_added)
        self.hal_manager.connect_to_signal('DeviceRemoved', 
                                           self.on_device_removed)

        self.udi_dict = {}
        self.modify_handler_dict = {}
        self.devicelist = DeviceList()

        self.__init_actors()

        if with_cold:
            coldplug = ColdPlugListener(self)
            coldplug.start()

        self.logger.info(_("Device Listener started"))


    def on_device_added(self, udi, *args):
        """
        [es] Cuando se detecta la conexión de un nuevo dispositivo se
             identifica el actor y se invoca el metodo on_added del mismo.
             Si no se reconoce el dispositivo se muestra un mensaje generico
             de "Dispositivo Desconocido Conectado"
        -----------------------------------------------------------------------
        [en] When a new device connection is detected we try to identify
             the corresponding actor and we launch its on_added method.
             If device is not recognized then we show up a generic "Unknown
             Device Connected" message
        """
        self.logger.debug(_("Device Added") + ": " + str(udi))
        self.devicelist.save()

        obj = self.bus.get_object('org.freedesktop.Hal', udi)
        obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

        properties = obj.GetAllProperties()
        print
        print
        print _("Connected") + " ################################"
        self.__print_properties(properties)

        actor = self.get_actor_from_properties(properties)

        if actor: 
            try:
                actor.on_added()
            except:
                self.logger.warning(str(traceback.format_exc()))
            #    self.message_render.show_warning(_("Warning"),
            #                    _("Unknown Device Connected")+".")



    def on_device_removed(self, udi, *args): 
        """
        [es] Cuando se detecta la desconexion de un dispositivo se invoca
             el metodo on_removed definido para el actor correspondiente.
             Si no se reconoce el dispositivo se da un mensaje genérico de 
             "Dispositivo Desconocido Desconectado"
        -----------------------------------------------------------------------
        [en] When a device disconnection is detected we launch the on_removed
             method defined for the corresponding actor. If device is not 
             recognized then we show up a generic "Unknown Device Removed" message
        """
        self.logger.debug(_("Device Removed") + ": " + str(udi))
        self.devicelist.save()

        if self.udi_dict.has_key(udi):
            disp = self.udi_dict[udi]
            try:
                disp.on_removed()
            except:
                self.logger.warning(str(traceback.format_exc()))
            print
            print
            print _("Disconnected") + " ################################"
            self.__print_properties(disp.properties)
            del self.udi_dict[udi]
        else:
            self.message_render.show_warning(_("Warning"),
                                             _("Unknown Device Removed") + ".")


    def on_property_modified(self, udi, num, values):
        """
        [es] Cuando se detecta la modificación de una propiedad de un
             dispositivo conectado se invoca el metodo on_property_modified
             definido para el actor correspondiente
        -----------------------------------------------------------------------
        [en] When a property modification from a connected device is detected
             we launch the on_property_modified method defined for the 
             corresponding actor        
        """
        for ele in values:
            key = ele[0]

            if self.udi_dict.has_key(udi):
                # [es] Actualizamos las propiedades del objeto actor
                # [en] Actualize actor object properties
                actor = self.udi_dict[udi]
                obj = self.bus.get_object('org.freedesktop.Hal', udi)
                obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

                actor.properties = obj.GetAllProperties()

                print
                print
                print "#############################################"
                print _("Property Modified:")
                print _("udi:"), udi
                print key, ':', actor.properties[key]
                print "#############################################"
                try:
                    actor.on_modified(key)
                except Exception, e:
                    self.logger.warning(str(traceback.format_exc()))


    def get_actor_from_properties(self, prop):
        """
        [es] Devuelve un actor que encaje con las propiedades espeficicadas
             en prop
        -----------------------------------------------------------------------
        [en] Returns an actor that matches the especified properties in prop
        """
        klass = None
        actor_klass = None

        # [es] prioridad -> 1     2     3     4     5 
        # [en] priority  -> 1     2     3     4     5
        priority_actors = [None, None, None, None, None]
        priority_counts = [0, 0, 0, 0, 0]

        import actors
        for klass in actors.ACTORSLIST:
            # [es] Ponemos prioridad a 3 si no esta entre 1 y 5
            # [en] Set priority to 3 if not in 1 to 5 range
            if klass.__priority__ not in (1, 2, 3, 4, 5):
                klass.__priority__ = 3

            kpriority = klass.__priority__ - 1
            count = self.__count_equals(prop, klass.__required__)
            if count > priority_counts[kpriority]:
                priority_counts[kpriority] = count
                priority_actors[kpriority] = klass

        for i in  (4, 3, 2, 1, 0):
            if  priority_actors[i]: 
                if priority_actors[i].__enabled__:
                    actor_klass = priority_actors[i]
                else: 
                    # [es] Activamos el actor de nuevo para que pueda ser 
                    #      comprobado en la proxima consulta
                    # [en] Enable the actor again to check it in next polling
                    priority_actors[i].__enabled__ = True	
                break

        actor = None 
        udi = prop['info.udi']
        if actor_klass:
            actor = actor_klass(self.message_render, prop)
            self.udi_dict[udi] = actor
            if not self.modify_handler_dict.has_key(udi):
                self.modify_handler_dict[udi] = \
                           lambda *args: self.on_property_modified(udi, *args) 
                self.bus.add_signal_receiver(self.modify_handler_dict[udi],
                    dbus_interface = 'org.freedesktop.Hal.Device',
                    signal_name = "PropertyModified",
                    path = udi)
        else:
            # [es] Configuracion del registro abreviada (en los actores, 
            #      logging.getLogger debe ser invocado tras la funcion main
            # [en] Shorting logger setup (in module actors, logging.getLogger 
            #      must be invoked _after_ than in main function).
            from actors.deviceactor import DeviceActor
            actor = DeviceActor(self.message_render, prop)
            self.udi_dict[udi] = actor

        return actor


    def __print_properties(self, properties):
        """
        [es] Imprime las propiedades del dispositivo
        -----------------------------------------------------------------------
        [en] Prints device properties
        """
        print 
        print '-----------------------------------------------'
        print _("Device") + ":", properties['info.udi']
        print 
        keys = properties.keys()
        keys.sort()

        for key in keys:
            print key + ':' + str(properties[key])


    def __count_equals(self, prop, required):
        """
        [es] Devuelve el número de coincidencias entre el diccionario prop y
             required, siempre y cuando TODOS los elementos de required estén 
             en prop. En caso contrario devuelve 0.
        -----------------------------------------------------------------------
        [en] Returns the matching number of elements between prop and 
             required, only if ALL elements from required are in prop.
             Otherwise it returns 0.
        """
        count = 0
        for key in required.keys():
            if not prop.has_key(key): 
                return 0

            value =  prop[key]
            # [es] Evaluamos expresiones de python requeridas
            # [en] Eval required python expressions
            reqvalue = required[key]
            if isinstance(reqvalue,  str) and \
                    reqvalue.strip().startswith('python:'):
                expression = reqvalue.strip()[7:]
                if not eval(expression):
                    return 0

            # [es] Añadimos soporte para metodos y funciones
            # [en] Add support for methods and functions
            elif isinstance(reqvalue, types.FunctionType) or \
                    isinstance(reqvalue, types.MethodType):
                if not reqvalue(value):
                    return 0

            else:
                if prop[key] != required[key]:
                    return 0
            count += 1

        return  count


    def __init_actors(self):
        """
        [es] Inicializamos los actores
        -----------------------------------------------------------------------
        [en] Initialize actors
        """
        obj = self.bus.get_object('org.freedesktop.Hal',
                                  '/org/freedesktop/Hal/Manager')
        manager = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')

        for udi in manager.GetAllDevices():
            obj = self.bus.get_object('org.freedesktop.Hal', udi)
            obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')

            properties = obj.GetAllProperties()
            self.get_actor_from_properties(properties)


def main():
    """
    [es] Inicialización de Hermes.
         Se siguen los siguientes pasos:
             1. Inicialización del subsistema de soprte a i18n
             2. Lectura de parametros de configuracion
             3. Segun los parametros ponemos en marcha el modo de 
                funcionamiento correspondiente:
                        -d: Registro a nivel DEPURACION
                    sin -d: Registro a nivel INFORMACION
                        -c: Captura de Log
                    sin -c: MODO PASIVO
             4. Lanzamiento de Hermes
    ---------------------------------------------------------------------------
    [en] Hermes initialization.
         We follow the next steps:
             1. i18n support subsystem initialization
             2. Configuration params reading
             3. Depending on the params we need to setup the corresponding
                operation mode:
                       -d: DEBUG log level
                    no -d: INFO log level 
                       -c: Log Capture
                    no -c: PASIVE MODE
             4. Hermes launch
    """
    # 1.
    # [es] Intentamos inicializar el soporte de multiples idiomas de hermes
    #      Si falla, mostramos un error en ingles y continuamos la ejecución
    #      de hermes sin soporte de i18n. En este caso, la interfaz se 
    #      mostrará en ingles únicamente.
    # [en] We try to start and configure hermes' multiple languages support
    #      If we fail, we show up an english error message and continue with
    #      hermes execution without i18n support. In this case, interface will
    #      show in english only.
    try:
        import defs
        setup_gettext('hermes-hardware', defs.DATA_DIR)
    except ImportError:
        print 'WARNING: Running uninstalled, no gettext support'

    # 2.
    # [es] Extraemos las opciones de configuración de los argumentos 
    #      pasados por la linea de comandos.
    # [en] We extract configuration options from the commands line
    #      arguments
    parser = OptionParser(usage = _('usage: %prog [options]'))
    parser.set_defaults(debug = False)
    parser.set_defaults(capture_log = False)

    parser.add_option('-d', '--debug', 
            action = 'store_true',
            dest = 'debug',
            help = _('Starts in debug mode.'))

    parser.add_option('-c', '--capture-log',
            action = 'store_true',
            dest = 'capture_log',
            help = _('Capture device logs.'))

    (options, args) = parser.parse_args()
    del args

    # 3. 
    # [es] Activamos el registro de actividad a nivel de depuración si se 
    #      recibió el parámetro -d o a nivel informativo si no se recibio -d.
    #      Iniciamos en modo captura de cadenas de identificación de hardware 
    #      si se recibio -c o en modo pasivo en caso contrario
    # [en] We start activity log in debug mode if we got -d param or in info
    #      mode if we didn´t.
    #      We start in hardware identification strings capture mode if we got
    #      -c param or in passive mode otherwise.
    
    if options.debug:
        level = logging.DEBUG
    else:
        level = logging.INFO

    logfilename = '/var/tmp/hermes-hardware-' + \
                  os.environ['USER'] + str(os.getuid()) + '.log' 

    logging.basicConfig(level = level,
            format='%(asctime)s %(levelname)s %(message)s',
                    filename = logfilename,
                    filemode='a')

    if options.capture_log:
        filepath = '/var/tmp/filenotification-' + \
                os.environ['USER'] + str(os.getuid()) + \
                '.log'
        iface = FileNotification(filepath)
        capture_log_gui = CaptureLogGui()
    else:
        iface = NotificationDaemon()

    logging.getLogger().info(_("------------ Hermes started."))

    # 4.
    # [es] Iniciamos el dispositivo de escucha, creamos el icono en la barra
    #      de iconos del escritorio e iniciamos soporte multihilo para Hermes.
    #      Finalmente lanzamos el proceso principal de la aplicacion GTK.
    # [en] We start devices listener, create an icon inside TrayIcon Bar and
    #      start multithreading support for Hermes.
    #      Finally we launch the main GTK application process.
    
    global DeviceActor
    from actors.deviceactor import DeviceActor

    DeviceListener(iface, with_cold = False)
    HermesTrayIcon()
    gtk.gdk.threads_init()
    try:
        gtk.main()
    except:
        # [es] Antes de terminar debemos cerrar el fichero de registro de 
        #      dispositivos
        # [en] Before finishing we must close the device log file
        if 'capture_log_gui' in locals():
             capture_log_gui.logfile.close()

        logging.getLogger().info(_("------------ Hermes finished."))


if __name__ == "__main__":
    main()


