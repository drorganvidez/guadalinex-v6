# -*- coding: utf-8 -*-
# Configuración útil para master.cfg

############
# SVN 
############

# URL del subversion sobre el que hacer polling.
svn = "http://forja.guadalinex.org/guadalinexv6"

# Tiempo de polling, en segundos, sobre el subversion para detectar cambios.
polling_time = 2*60

# Nombre del directorio que contendrá las apps. 
# Las apps son ramas de subversion con tags y trunk y que se construyen 
# con debuild. Solo se chequeará la última versión el tag sobre la que se
# hayan aplicado commits. 
apps_dir = "apps"

# Nombre del directorio que contendrá los metapkgs.
# Los metapkgs son ramas de subversion a construir con gcs_build.
metapkgs_dir = "metapkgs"

# Nombre de la subrama trunk.
trunk_dir = "trunk"

# Nombre de la subrama tags.
tags_dir = "tags"

# Nombre de la subrama gcs.
gcs_dir = "gcs"

# Lista de nombre de las apps. El nombre debe coincidir con la rama de 
#subversion que contiene la app. La inclusión en esta lista de una nueva app
#hace que buildbot la gestione automáticamente.
#apps=[]
apps=[
        "sun-java6",
#	"buildbotdummy",
        "casper-guada",
	"ca-certificates-java",
	"diagnostic-report",
#	"dumphive",
#        "escritorio-movistar",
	"extras-installer",
#        "g3g",
        "gcs",
	"gedit-plugin-tloleo",
	"getatr",
        "gfxboot-theme-guada",
	"guadafox",
	"guadalinex-eadmin",
        "guadalinex-keyring",
#        "guadalinex-supplement-generator",
#        "guadalinex-supplement-installer",
	"gru",
	"grub",
#        "hermes",
	"java-common",
        "lemurae",
#        "lig",
#	"ubiquity",
        "usplash-theme-guadalinex",
#        "vodafone-mobile-connect-card-driver-for-linux",
#        "accesibility-profiles",
#        "gedit-plugin-tloleo",
#        "gnome-panel",
#        "gnome-system-tools",
#        "gnome-volume-manager",
#        "gru",
#        "grubaker",
        "python-syck",
        "guada-ubiquity",
        "mount-systray",
	"rarian"
#        "opensc",
#        "watermain",
]

# Lista de nombre de los metapkgs. El nombre debe coincidir con la rama de 
# subversion que contiene el metapkg. La inclusión en esta lista de un nuevo 
# metapkg hace que buildbot lo gestione automáticamente.
metapkgs = [
	"guadalinex-about",
        "guadalinex-artwork",
        "guadalinex-desktop",
        "guadalinex-desktop-conf",
#	"guadalinex-example-content",
        "guadalinex-minimal",
        "guadalinex-minimal-conf",
        "guadalinex-standard",
#        "guadalinex-standard-conf",
#	"guadalinex-user-manual",
        "meta-guadalinex-v6",
#        "suplemento-dvd-gv5",
#        "suplemento-gv5-desarrollo",
#        "suplemento-gv5-educativo",
#        "suplemento-gv5-juegos",
#        "suplemento-gv5-varios",
]


# Building 
############

# Tiempo de cortesía, en segundos,  entre que se detecta un cambio en el último
# tag de la app y se comienza el proceso de integración.
app_timer = 5

# Tiempo de cortesía, en segundos, entre que se detecta un cambio en el metapkg
# y se comienza el proceso de integración.
metapkg_timer = 5

# Gensys es ejecutado una vez al día. Defínase aquí la hora concreta de lanzamienzo.
gensys_time = "00:00"

# Indica si debemos abortar el proceso de integración ante errores 
# de lintian.
halt_on_lintian_error = False

# Indica si debemos abortar el proceso de integración ante errores
# de unittests.
halt_on_unittest_error = True


################
# Gensys
################

# Directorio donde se subirán automáticamente los paquetes construidos.
upload_dir = "/var/gensys/deb-repositories/gv6"

# TODO: Esto debería ir en una clase a FileUpload a parte
rawimage = "/var/gensys/live-helper/guadalinexv6/binary.iso"
ftpimage = "/var/gensys/guadalinex-desktop-i386.iso"

# Path común para la ejecución de los scripts gensys
path = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Script para generar el repositorio 'derivative' y variables de entorno
# que necesite para su ejecución
derivative = "update-derivative-repository"
derivative_env = {
    "PATH" : path
}

# Script live-helper y variables de entorno que necesite para su ejecución
livehelper = "/var/gensys/live-helper/guadalinexv6/build.sh"
livehelper_env = { 
    "PATH" : path
}

# pdebuild custom command
pdebuild = "pdebuild -- --basepath /var/gensys/cowbuilder/base-test.cow"
