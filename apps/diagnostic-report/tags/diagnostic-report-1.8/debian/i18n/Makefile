# Copyright 2007 Miriam Ruiz <little_miry@yahoo.es>
# Copyright 2007 Jens Seidel <jensseidel@users.sf.net>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.

LOCALEDIR=./

all: diagnostic-report.pot build-stamp

diagnostic-report.pot:
	@cat languages.list | while read lang enc; do \
		echo "Compiling '.po' files..."; \
		msgfmt -o $$lang.mo $$lang.po ; \
	done

build: build-stamp

build-stamp: diagnostic-report.pot

clean:
	rm -f *.mo
	rm -f build-stamp

install: build-stamp
	@cat languages.list | while read lang enc; do \
		echo Installing \"$$lang\" translation; \
		install -p -d -m 755 $(LOCALEDIR)$$lang/LC_MESSAGES ; \
		install -m 644 $$lang.mo $(LOCALEDIR)$$lang/LC_MESSAGES/diagnostic-report.mo ; \
		encdir=""; [ "$$enc" = utf-8 ] && encdir=.UTF-8; \
	done
