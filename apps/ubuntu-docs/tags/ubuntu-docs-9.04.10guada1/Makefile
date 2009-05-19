####################################################################################           
# Makefile for the GNOME Ubuntu Documentation
# Copyright (C) 2005-2006 Ubuntu Documentation Project (ubuntu-doc@lists.ubuntu.com)
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version. 
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#    On Debian based systems a copy of the GPL can be found 
#    at /usr/share/common-licenses/GPL
#
####################################################################################

MAKECMD=make

# XSL Processors
XSLTPROC=/usr/bin/xsltproc

current_distro=$(shell test -e /etc/debian_version && echo "debian")

# NWalsh Docbook XSL's
ifeq ($(current_distro), debian)
# Ubuntu
NWDBXSL=/usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl

# Debian and Ubuntu also need an explicit location for the XML catalog files
#export XML_CATALOG_FILES = /usr/share/xml/docbook/schema/dtd/4.1.2/catalog.xml
#else
# SuSE
#NWDBXSL=/usr/share/xml/docbook/stylesheet/nwalsh/current/html/docbook.xsl
endif

# Makes an Image list text file
MKIMGLST=libs/imagelist.xsl

# Collected and Write Status
wOS=libs/writeOwnerStatus.xsl

# Ubuntu Docbook Customization Layer

UBUNTUCHUNKXSL=libs/ubuntu-html-chunk-cust.xsl
UBUNTUSINGLEXSL=libs/ubuntu-html-single-cust.xsl
PDFSTYLE=libs/pdf/ubuntu-pdf.xsl
LULUSTYLE=libs/pdf/ubuntu-pdf-lulu.xsl
# Local path to newer xsl for use with fop 0.90
PDFSTYLE2=libs/pdf/ubuntu-pdf2.xsl

# Base gnome directories for output from processor
BASE=build/

.PHONY: website switching

gdeb: 

all: clean style index serverguide switching status contributors

	for doc in `cat libs/shipped-docs`; do xsltproc --xinclude -o $(BASE)$$doc/C/index.html $(UBUNTUCHUNKXSL) $$doc/C/$$doc.xml; sed -i $(BASE)$$doc/C/*legal.html -e "s#\.\./libs/C/contributors\.xml#libs/C/contributors\.html#g"; done

index:

	xsltproc --stringparam html.stylesheet "libs/ubuntu-book.css" -o $(BASE)index.html $(UBUNTUCHUNKXSL) index.xml

clean:
	rm -rf $(BASE)*

style:

	# copy style sheet and common images to build directory
	mkdir -p build/libs/img
	mkdir -p build/libs/admon
	mkdir -p build/libs/callouts
	mkdir -p build/libs/navig
	cp libs/*css build/libs/
	cp libs/img/*png build/libs/img/
	cp -r libs/admon/*.* build/libs/admon	
	cp -r libs/callouts/*.* build/libs/callouts
	cp -r libs/navig/*.* build/libs/navig

## Targets for building standalone documents

switching:

	xsltproc --stringparam html.stylesheet "libs/ubuntu-book.css" --stringparam navig.graphics.path "images/navig/" --stringparam callout.graphics.path "images/callouts/" --stringparam admon.graphics.path "images/admin/" --xinclude -o $(BASE)switching/index.html $(UBUNTUCHUNKXSL) switching/C/switching.xml

	# copy style sheet and common images to build directory
	mkdir -p $(BASE)switching/libs/img
	cp libs/*css $(BASE)switching/libs/
	cp libs/img/*png $(BASE)switching/libs/img/
	mkdir -p $(BASE)switching/images/admon
	cp -r libs/admon/*.* $(BASE)switching/images/admon	
	mkdir -p $(BASE)switching/images/callouts
	cp -r libs/callouts/*.* $(BASE)switching/images/callouts	
	mkdir -p $(BASE)switching/images/navig
	cp -r libs/navig/*.* $(BASE)switching/images/navig	

serverguide: style

	xsltproc --xinclude -o $(BASE)serverguide/C/index.html $(UBUNTUCHUNKXSL) serverguide/C/serverguide.xml
	sed -i $(BASE)serverguide/C/*legal.html -e "s#\.\./libs/C/contributors\.xml#libs/C/contributors\.html#g"


status: style

	xsltproc --xinclude -o $(BASE)status/sg-report.xml $(wOS) serverguide/C/serverguide.xml
	xsltproc --xinclude -o $(BASE)status/sg-report.html $(NWDBXSL) $(BASE)status/sg-report.xml

contributors: style

	xsltproc --stringparam root.filename "contributors" -o $(BASE)libs/C/ $(UBUNTUCHUNKXSL) libs/C/contributors.xml

index-test: style

	xsltproc --xinclude -o $(BASE)index-test/ $(UBUNTUCHUNKXSL) index2.xml
	sed -i $(BASE)index-test/*.html -e "s#ghelp:add-applications#add-applications.html#g"

#	sed -i $(BASE)index-test/*.html -e "s#ghelp:administrative##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:users-admin##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:basic-commands##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:programming##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:user-guide\#panels##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:user-guide\#menubar##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:user-guide\#prefs##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:desktop-effects##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:add-applications\#synaptic##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:hardware\#restricted-manager##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:user-guide\#nautilus##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:hardware\#disks##g"
#
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#	sed -i $(BASE)index-test/*.html -e "s#ghelp:server##g"
#

