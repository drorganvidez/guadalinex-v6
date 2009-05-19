#!/bin/sh

####################################################################################           
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
####################################################################################

# We have some different groups of documentation for the purposes of making
# the pot files

# Group one - shipped docs
for x in `cat libs/shipped-docs`; do
	echo ${x}
	xml2po -e -o ${x}/po/${x}.pot ${x}/C/*.xml ${x}/C/*-C.omf
done

# Group two - other docs

	echo server
	xml2po -e -o ../generic/serverguide/po/serverguide.pot ../generic/serverguide/C/*xml ../generic/serverguide/C/*omf

