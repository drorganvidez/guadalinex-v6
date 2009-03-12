#!/bin/bash

check_n_umount() {
   VOLATILE=$(cat /proc/mounts|grep -e "chroot.*generic/volatile"|awk '{print $2}')
   if [ ! -z "$VOLATILE" ]
   then
   	umount $VOLATILE
   fi
}
LH_PATH=/var/gensys/live-helper/guadalinexv6
BUILD_DATE=$(date +%Y%m%d-%H:%M)
LOG_FILE="/var/log/lh_build-$BUILD_DATE.log"
ERROR_LOG_FILE="/var/log/lh_build-$BUILD_DATE.error.log"
test -h /var/log/lh_build.log && rm /var/log/lh_build.log
ln -s $LOG_FILE /var/log/lh_build.log
test -h /var/log/lh_build.error.log && rm /var/log/lh_build.error.log
ln -s $ERROR_LOG_FILE /var/log/lh_build.error.log

cd $LH_PATH
rm -rf chroot cache .stage
check_n_umount
lh_clean
lh_build 2>$ERROR_LOG_FILE | tee -a $LOG_FILE
EXIT_VALUE=$PIPESTATUS
test -f binary.iso && chmod 755 binary.iso
check_n_umount
cd -
exit $EXIT_VALUE
