#!/usr/bin/make -f

DOMAIN=diagnostic-report

all: build install

$(DOMAIN).pot: merge-po
	xgettext -L Shell -o $(DOMAIN).pot $(top_srcdir)/$(DOMAIN)

build:
	@cat languages.list | while read lang enc; do \
		echo "Compiling '.po' files..."; \
		msgfmt -o $$lang.mo $$lang.po ; \
	done

merge-po:
	@cat languages.list | while read lang enc; do \
		intltool-update -r --dist $$lang ; \
	done

clean:
	rm -f *.mo
	rm -rf locale
	rm -f build-stamp

install:
	@cat languages.list | while read lang enc; do \
		echo Installing \"$$lang\" translation; \
		install -v -p -d -m 755 $(LOCALEDIR)$$lang/LC_MESSAGES ; \
		install -v -m 644 $$lang.mo $(LOCALEDIR)$$lang/LC_MESSAGES/$(DOMAIN).mo ; \
	done

