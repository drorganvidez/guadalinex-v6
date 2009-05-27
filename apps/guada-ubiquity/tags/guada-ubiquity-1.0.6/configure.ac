AC_INIT([guada-ubiquity],[0.9],[jojeda@emergya.es])
AC_PREREQ([2.61])
AC_CONFIG_HEADERS([config.h])
AM_INIT_AUTOMAKE([-Wall -Werror foreign])

GNOME_COMMON_INIT


dnl check for python
dnl ----------------------------
AM_PATH_PYTHON

PKG_CHECK_MODULES(PYGTK, pygtk-2.0 >= 2.6)
AC_SUBST(PYGTK_CFLAGS)
AC_SUBST(PYGTK_LIBS)

PKG_CHECK_MODULES(PYDBUS, dbus-python >= 0.80)
AC_SUBST(PYDBUS_CFLAGS)
AC_SUBST(PYDBUS_LIBS)

dnl check for libglade
dnl -----------------------------------------
AC_MSG_CHECKING([for gtk.glade])
prog="
import sys
try:
  import gtk.glade
except RuntimeError:
  sys.exit(0)
except ImportError:
  sys.exit(1)
sys.exit(0)
"

if $PYTHON -c "$prog" 1>&AC_FD_CC 2>&AC_FD_CC
then
  AC_MSG_RESULT([found])
else
  AC_MSG_RESULT([not found])
  AC_MSG_ERROR([You need to have python libglade bindings installed])
fi

AC_SUBST(VERSION)
AC_SUBST(PACKAGE)

AC_CONFIG_SRCDIR([src/frontend/guada_ui.py])
AC_CONFIG_FILES([
Makefile
data/Makefile
data/glade/Makefile
data/pics/Makefile
data/desktop/Makefile
src/Makefile
src/automatically_partition/Makefile
src/automatically_partition/70reuse/Makefile
src/frontend/Makefile
src/DiskPreview/Makefile
src/scripts/Makefile
src/ubiquity-init/Makefile
])
AC_OUTPUT

echo
echo $PACKAGE v$VERSION
echo

echo Prefix............... : $prefix

echo "Now type make to compile"
echo "Then su to root and type: make install"
echo
