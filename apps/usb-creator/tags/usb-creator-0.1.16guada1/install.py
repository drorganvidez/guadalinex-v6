#!/usr/bin/python
import getopt
import os
import stat
import sys
import shutil

def main(source, target):
    # TODO: debate pulling the total_size bit in from ubiquity for more
    # accurate progress.
    # TODO: Fedora's program shells out to cp and uses another thread that
    # checks the free space on the drive and updates the UI accordingly.
    # Is this worth replicating?

    # Some of the code in this function was copied from Ubiquity's
    # scripts/install.py

    if not os.path.exists(source) or not os.path.exists(target):
        sys.exit(1)
    walklen = 0
    percent = 0.0
    for dirpath, dirnames, filenames in os.walk(source):
        for name in dirnames + filenames:
            walklen += 1
    inc = 100.0 / walklen
    for dirpath, dirnames, filenames in os.walk(source):
        sp = dirpath[len(source) + 1:]
        for name in dirnames + filenames:
            relpath = os.path.join(sp, name)
            sourcepath = os.path.join(source, relpath)
            targetpath = os.path.join(target, relpath)
            st = os.lstat(sourcepath)
            mode = stat.S_IMODE(st.st_mode)
            if stat.S_ISLNK(st.st_mode):
                if os.path.lexists(targetpath):
                    os.unlink(targetpath)
                linkto = os.readlink(sourcepath)
                #os.symlink(linkto, targetpath)
                # FIXME: Handle this somehow?
                #print 'trying to symlink %s' % linkto
                pass
            elif stat.S_ISDIR(st.st_mode):
                if not os.path.isdir(targetpath):
                    os.mkdir(targetpath, mode)
            elif stat.S_ISCHR(st.st_mode):
                os.mknod(targetpath, stat.S_IFCHR | mode, st.st_rdev)
            elif stat.S_ISBLK(st.st_mode):
                os.mknod(targetpath, stat.S_IFBLK | mode, st.st_rdev)
            elif stat.S_ISFIFO(st.st_mode):
                os.mknod(targetpath, stat.S_IFIFO | mode)
            elif stat.S_ISSOCK(st.st_mode):
                os.mknod(targetpath, stat.S_IFSOCK | mode)
            elif stat.S_ISREG(st.st_mode):
                if os.path.exists(targetpath):
                    os.unlink(targetpath)
                try:
                    sourcefh = open(sourcepath, 'rb')
                    targetfh = open(targetpath, 'wb')
                    # TODO: md5 check.  Copy error handling.
                    shutil.copyfileobj(sourcefh, targetfh)
                finally:
                    sourcefh.close()
                    targetfh.close()
                #print '%s -> %s' % (sourcepath, targetpath)
            percent = percent + inc
            # TODO: self.frontend.progress(percent)
            print '%d' % percent
            #self.frontend.progress(percent)

if __name__ == '__main__':
    source = ''
    target = ''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 's:t:')
    except getopt.GetoptError:
        sys.exit(1)
    for opt, arg in opts:
        if opt == '-s':
            source = arg
        elif opt == '-t':
            target = arg
    #print '%s %s' % (source, target)
    main(source, target)
