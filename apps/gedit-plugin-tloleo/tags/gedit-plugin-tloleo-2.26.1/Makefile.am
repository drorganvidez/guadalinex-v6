SUBDIRS = plugins po

ACLOCAL_AMFLAGS = -I m4

EXTRA_DIST =			\
	autogen.sh		\
	ChangeLog  		\
	gnome-doc-utils.make	\
	intltool-extract.in 	\
	intltool-merge.in 	\
	intltool-update.in

DISTCLEANFILES = 		\
	configure		\
	aclocal.m4		\
	gnome-doc-utils.make	\
	intltool-extract 	\
	intltool-merge 		\
	intltool-update		\
	m4/intltool.m4		\
	po/Makefile.in.in	\
	Makefile.in

DISTCHECK_CONFIGURE_FLAGS = --with-plugins=really-all
