#!/usr/bin/make -f

all: build install

build: 
	$(MAKE) -C po LOCALEDIR=$(CURDIR)/po/locale/

install:
	$(MAKE) -C po install LOCALEDIR=$(CURDIR)/po/locale/

clean:
	$(MAKE) -C po clean
