# -*- coding: utf-8 -*-
#
# Authors:
#     Original creators of hermes v1: Unknown
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo device_list - Controles GTK para el asistente en frio 
# [en] hermes_hardware module - Coldassistant GTK widgets
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



import gtk
import dbus
import os
import thread
import threading
import time

from gettext import gettext as _

from actors import ACTORSLIST
from actors.deviceactor import DeviceActor
from actors.deviceactor import PkgDeviceActor
from actors import usbdevice
from utils.notification import FileNotification
from hermes_hardware import DeviceListener


class DeviceList(gtk.VBox):
    """ 
    [es] Es un control GTK de tipo treeview con otro de tipo liststorage para 
         mostrar la información de los actores y dispositivos identificados por 
	 Hermes
    ---------------------------------------------------------------------------
    [en] It is treeview GTK widget with a liststorage for keep information 
         about Hermes identified actors and devices.
    """
    __instance__ = None

    def __init__(self):
        """ 
        [es] Método de inicializacion del control
        -----------------------------------------------------------------------
        [en] Widget init method
        """ 
	gtk.VBox.__init__(self, spacing = 10)

    @staticmethod
    def get_instance():
        """ 
        [es] Devuelve atributo privado __instance__
        -----------------------------------------------------------------------
        [en] Returns private attribute __instance__
        """ 
        if not DeviceList.__instance__:
            DeviceList.__instance__ = DeviceList()
        return DeviceList.__instance__


    def reset(self):
        """ 
        [es] Método de actualizacion del contenido del control
        -----------------------------------------------------------------------
        [en] Widget content refresh method
        """ 
        for child in self.get_children():
            self.remove(child)

        self._populate()


    def _populate(self):
        """
        [es] Método par
        -----------------------------------------------------------------------
        [en] 
        """ 
        while gtk.events_pending():
            gtk.main_iteration()

        device_listener = DeviceListener(FileNotification('/dev/null'),
                                         with_cold = False)
        bus = dbus.SystemBus()
        obj = bus.get_object('org.freedesktop.Hal',
                             '/org/freedesktop/Hal/Manager')
        manager = dbus.Interface(obj, 'org.freedesktop.Hal.Manager')
        progressbar = gtk.ProgressBar()
        progressbar.set_fraction(0)
        progressbar.set_text(_('Searching for devices...'))

        self.pack_start(progressbar)
        self.show_all()
        while gtk.events_pending():
            gtk.main_iteration()

        good_actors = []

        for udi in manager.GetAllDevices():
            obj = bus.get_object('org.freedesktop.Hal', udi)
            obj = dbus.Interface(obj, 'org.freedesktop.Hal.Device')
            properties = obj.GetAllProperties()
            actor = device_listener.get_actor_from_properties(properties)
            if actor and self._actor_is_good(actor):
                good_actors.append(actor)

        total = len(good_actors)
        i = 1
        actor_renderers = []
        if not good_actors:
            self.remove(progressbar)
            msg = _("Sorry, can't find any device with actions asociated.")
            label = gtk.Label(msg)
            label.set_line_wrap(True)
            self.pack_start(label)
            self.show_all()
            return

        for good_actor in good_actors:
            progressbar.set_fraction(i / float(total))
            while gtk.events_pending():
                gtk.main_iteration()
            i += 1
            actor_renderers.append(ActorRenderer(good_actor))

        self.remove(progressbar)
        for renderer in actor_renderers:
            self.pack_start(renderer)
        self.show_all()


    def _actor_is_good(self, actor):
        """ 
        [es] Indica si el actor tiene acciones asociadas Devuelve valor booleano
        -----------------------------------------------------------------------
        [en] Say if actor has associated actions. Returns boolean value

        """ 
        if actor.__dict__.get('__packages__', None):
            return True

        if issubclass(actor.__class__, PkgDeviceActor):
            return True

        return False



class  ActorRenderer(gtk.VBox):
    """ 
    [es] 
    ---------------------------------------------------------------------------
    [en] 
    """

    def __init__(self, actor):
        """
        [es] Método de inicializacion del control
        -----------------------------------------------------------------------
        [en] Widget init method
        """
        gtk.VBox.__init__(self, spacing = 10)

        self.label = gtk.Label()
        self.image = gtk.Image()
        self.actor = actor
        self.hbox = gtk.HBox()

        self._configure()
        self.show_all()


    def _configure(self):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        actor = self.actor.__class__(self, self.actor.properties)
        actor.on_added()

    # [es] Interfaz de Notificaciones
    # [en] Notification interface 

    def show (self, summary, body, icon, actions = {}):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        if not actions:
            return 

        # [es] Icono
        # [en] Icon
        if os.sep in icon:
            self.image.set_from_file(icon)
        else:
            self.image.set_from_stock(icon, gtk.ICON_SIZE_DIALOG)

        self.hbox.pack_start(self.image, False, False)

        # [es] Texto
        # [en] Text
        self.label.set_text(summary)
        self.hbox.pack_start(self.label, False, False)

        # [es] Acciones
        # [en] Actions
        action_vbox = gtk.VBox()
        for text, action in actions.items():
            actionrenderer = ActionRenderer(text, action)
            action_vbox.pack_start(actionrenderer, True, False)

        self.hbox.pack_start(action_vbox, True, False)

        self.pack_start(self.hbox)
        self.pack_start(gtk.HSeparator())


    def show_info(self, summary, body, actions = {}):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        self.show(summary, body, gtk.STOCK_DIALOG_INFO, actions)


    def show_warning(self, summary, body, actions = {}):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        self.show(summary, body, gtk.STOCK_DIALOG_WARNING, actions)


    def show_error(self, summary, body, actions = {}):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        self.show(summary, body, gtk.STOCK_DIALOG_ERROR, actions)



class ActionRenderer(gtk.Button):
    """ 
    [es]
    ---------------------------------------------------------------------------
    [en] 
    """

    def __init__(self, text, action):
        """
        [es] Método de inicializacion del control
        -----------------------------------------------------------------------
        [en] Widget init method
        """
        gtk.Button.__init__(self, text)
        self.connect('clicked', self.on_clicked)
        self.action = action

        self.show_all()


    def in_thread(self, event):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        os.system('touch /tmp/in_thread')
        os.system('echo in_thread >> /tmp/in_thread')
        self.action()
        event.set()


    def on_clicked(self, widget):
        """ 
        [es] 
        -----------------------------------------------------------------------
        [en] 
        """ 
        # Change label for a progress bar.
        pulse_bar = gtk.ProgressBar()
        pulse_bar.set_pulse_step(0.2)
        pulse_bar.show_all()
        label = self.get_child()
        self.remove(label)
        self.add(pulse_bar)
        pulse_bar.pulse()
        self.set_sensitive(False)

        # start thread
        event = threading.Event()
        thread.start_new_thread(self.in_thread, (event, ))
        while not event.isSet():
            while gtk.events_pending():
                gtk.main_iteration()
            pulse_bar.pulse()
            time.sleep(0.2)

        #self.remove(pulse_bar)
        #self.add(label)
        #self.set_sensitive(True)
        gtk.main_quit( )
