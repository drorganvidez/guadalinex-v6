# Makefile for the Generic Ubuntu documentation
# Jeff Schering <jeffschering@gmail.com>

# Base directories for output from processor
IMAGES=../build/generic/images/

# Server Guide
# NOTE: this target points to the actual makefile in the ubuntu directory 
server:
	make -C ../ubuntu -f Makefile server

# Packaging Guide
# NOTE: this target points to the actual makefile in the ubuntu directory 
package:
	make -C ../ubuntu -f Makefile package

# Style Guide
# NOTE: this target points to the actual makefile in the ubuntu directory 
sg:
	make -C ../ubuntu -f Makefile sg

# NOTE: this target points to the actual makefile in the ubuntu directory.
sg-pdf:

	make -C ../ubuntu -f Makefile sg-pdf

copy-files:
# Delete all images before copying them over from the repos. This is a 
# brute-force way of removing unused images from the build directory.
	rm -f $(IMAGES)*.*

	mkdir -p $(IMAGES)C
	cp -r images/C/*.* $(IMAGES)C

	mkdir -p $(IMAGES)admon
	cp -r ../common/admon/*.* $(IMAGES)admon
	
	mkdir -p $(IMAGES)callouts
	cp -r ../common/callouts/*.* $(IMAGES)callouts
	
	mkdir -p $(IMAGES)navig
	cp -r ../common/navig/*.* $(IMAGES)navig

	cp default.css ../build/generic/default.css
	
