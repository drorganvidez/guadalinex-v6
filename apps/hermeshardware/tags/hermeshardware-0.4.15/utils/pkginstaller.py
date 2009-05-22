# -*- coding: utf-8 -*-
#
# Authors: 
#     Guadalinex developers team
#     Jose Chaso (pchaso) <jose.chaso at gmail>
#
# [es] Modulo pkginstaller - Módulo para instalar paquetes
#      debian
# [en] pkginstaller module - Debian packages installer module
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


import apt_pkg
import subprocess
import os
import os.path

from utils.sudo import get_sudo
from gettext import gettext as _


class IPkgInstaller(object):
    """ 
    [es] Interfaz común para la instalación de paquetes
    -----------------------------------------------------------------------
    [en] Common interface for packages installers.
    """

    def check(self, pkg_list):
        """ 
        [es] Comprobamos si están instalados los paquetes de la lista
             pkg_list
             Devolvemos un booleano VERDADERO si todos los paquetes de la 
             lista pkg_list estan actualmente instalados en el sistema.
             En otro caso devolvemos FALSO.        
        -------------------------------------------------------------------
        [en] Check packages installation.
             Returns a TRUE boolean value if all the packages in pkg_list 
             are installed. Returns FALSE otherwise.
        """
        raise NotImplementedError


    def install(self, pkg_list):
        """ 
        [es] Instala todos los paquetes en pkg_list. Devuelve VERDADERO si
             la instalación no encuentra ningun error y FALSO en caso
             contrario.
        -------------------------------------------------------------------
        [en] Install all packages in pkg_list.
             Returns True if success. False otherwise.
        """
        raise NotImplementedError


class PkgInstaller(IPkgInstaller):
    """ 
    [es] Clase que implementa la interfaz IPkgInstaller
    -----------------------------------------------------------------------
    [en] Clase que implementa la interfaz IPkgInstaller
    """

    def __init__(self):
        """ 
        [es] Método de inicialización
        -------------------------------------------------------------------
        [en] Initialization method
        """
        # [es] Seleccionamos el instalador de paquetes (PkgInstaller)
        # [en] Select correct PkgInstaller
        config_path = os.path.abspath('actors/config/installer')
        installer_name = open(config_path).read().strip()
        if installer_name == 'synaptic':
            self.pkg_installer = SynapticInstaller()
        elif installer_name == 'rpm':
            self.pkg_installer = RpmInstaller()
        else:
            self.pkg_installer = SynapticInstaller()


    def check(self, pkg_list):
        """ 
        [es] Comprobamos si estan instalados todos los paquetes de la lista
             pkg_list
        -------------------------------------------------------------------
        [en] We check if all packages in pkg_list are installed
        """
        return  self.pkg_installer.check(pkg_list)

    
    def install(self, pkg_list):
        """ 
        [es] Instala todos los paquetes en pkg_list. Devuelve VERDADERO si
             la instalación no encuentra ningun error y FALSO en caso
             contrario.
        -------------------------------------------------------------------
        [en] Install all packages in pkg_list.
             Returns True if success. False otherwise.
        """
        return  self.pkg_installer.install(pkg_list)


class SynapticInstaller(IPkgInstaller):
    """ 
    [es] Clase que utiliza el instalador de paquetes debian apt
    -----------------------------------------------------------------------
    [en] Debian apt package installer class handler
    """

    def __init__(self):
        """ 
        [es] Método de inicialización
        -------------------------------------------------------------------
        [en] Initialization method
        """
        apt_pkg.init()

    def install(self, pkg_list):
        """ 
        [es] Instala todos los paquetes en pkg_list. Devuelve VERDADERO si
             la instalación no encuentra ningun error y FALSO en caso
             contrario.
        -------------------------------------------------------------------
        [en] Install all packages in pkg_list.
             Returns True if success. False otherwise.
        """
        if not get_sudo():
            return False

        cmd = ["/usr/bin/sudo", "/usr/sbin/synaptic", 
                "--hide-main-window",  "--non-interactive"]

        cmd.append("--set-selections")
        cmd.append("--progress-str")
        cmd.append(_("Installing packages"))
        cmd.append("--finish-str")
        cmd.append(_("Installed packages"))
        proc = subprocess.Popen(cmd, stdin = subprocess.PIPE)
        print proc
        f = proc.stdin

        for pkg in pkg_list:
            f.write("%s\tinstall\n" % pkg)
        f.close()
        proc.wait()
        return True


    def check(self, pkg_list):
        """ 
        [es] Devolvemos Verdadero si todos los paquetes de la lista
             pkg_list estan instalado. Falso en otro caso.
        -------------------------------------------------------------------
        [en] Return True if all packages in pkg_list are installed. False
             in other case.
        """
        #Collect the packages by name
        packages = apt_pkg.GetCache().Packages
        packages_dict = {}
        for pkg in packages:
            packages_dict[pkg.Name] = pkg

        #Check state
        for pkg_name in pkg_list:
            if (not packages_dict.has_key(pkg_name)) or \
                    (not packages_dict[pkg_name].CurrentVer):
                return False
        return True


class RpmInstaller(IPkgInstaller):
    """ 
    [es] 
    -----------------------------------------------------------------------
    [en] 
    """
    pass


if __name__ == "__main__":
    s = SynapticInstaller()
    s.check(['ifrench'])
    s.install(['ifrench'])
