all:

update-po:
	find -regex "./\(usbcreator\|scripts\|gui\).*\.\(py\|glade\)" > po/POTFILES.in
	echo ./desktop/usb-creator.desktop.in >> po/POTFILES.in
	python setup.py build_i18n --merge-po --po-dir po
