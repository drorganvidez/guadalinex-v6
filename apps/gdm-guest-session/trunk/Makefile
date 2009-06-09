GDMDIR=/usr/share/gdm/guest-session/
APPARMORDIR=/etc/apparmor.d/

check:
	for f in gdm/*; do sh -n $$f; done
	
install:
	install -d $(DESTDIR)$(GDMDIR) $(DESTDIR)$(APPARMORDIR)
	install -m 755 gdm/* $(DESTDIR)$(GDMDIR)
	install -m 644 apparmor/* $(DESTDIR)$(APPARMORDIR)

uninstall:
	for f in $(shell ls gdm); do rm -f $(DESTDIR)$(GDMDIR)$$f; done
	rmdir -p $(DESTDIR)$(GDMDIR) 2>/dev/null || true
	for f in $(shell ls apparmor); do rm -f $(DESTDIR)$(APPARMORDIR)$$f; done
	rmdir -p $(DESTDIR)$(APPARMORDIR) 2>/dev/null || true

clean:

.PHONY: install uninstall check clean
