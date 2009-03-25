/* main.c - experimental GRUB stage2 that runs under Unix */
/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 1999  Free Software Foundation, Inc.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 */

/* Simulator entry point. */
int grub_stage2 (void);

#include <stdio.h>
#include <getopt.h>
#include <unistd.h>
#include <string.h>
#include <stdlib.h>
#include <limits.h>

#define WITHOUT_LIBC_STUBS 1
#include "shared.h"

char *program_name = 0;
int use_config_file = 1;
int use_curses = 1;
int verbose = 0;
int read_only = 0;
static int default_boot_drive;
static int default_install_partition;
static char *default_config_file;

#define OPT_HELP -2
#define OPT_VERSION -3
#define OPT_HOLD -4
#define OPT_CONFIG_FILE -5
#define OPT_INSTALL_PARTITION -6
#define OPT_BOOT_DRIVE -7
#define OPT_NO_CONFIG_FILE -8
#define OPT_NO_CURSES -9
#define OPT_BATCH -10
#define OPT_VERBOSE -11
#define OPT_READ_ONLY -12
#define OPTSTRING ""

static struct option longopts[] =
{
  {"help", no_argument, 0, OPT_HELP},
  {"version", no_argument, 0, OPT_VERSION},
  {"hold", no_argument, 0, OPT_HOLD},
  {"config-file", required_argument, 0, OPT_CONFIG_FILE},
  {"install-partition", required_argument, 0, OPT_INSTALL_PARTITION},
  {"boot-drive", required_argument, 0, OPT_BOOT_DRIVE},
  {"no-config-file", no_argument, 0, OPT_NO_CONFIG_FILE},
  {"no-curses", no_argument, 0, OPT_NO_CURSES},
  {"batch", no_argument, 0, OPT_BATCH},
  {"verbose", no_argument, 0, OPT_VERBOSE},
  {"read-only", no_argument, 0, OPT_READ_ONLY},
  {0},
};


static void
usage (int status)
{
  if (status)
    fprintf (stderr, "Try ``grub --help'' for more information.\n");
  else
    printf ("\
Usage: grub [OPTION]...\n\
\n\
Enter the GRand Unified Bootloader command shell.\n\
\n\
    --batch                  turn on batch mode for non-interactive use\n\
    --boot-drive=DRIVE       specify stage2 boot_drive [default=0x%x]\n\
    --config-file=FILE       specify stage2 config_file [default=%s]\n\
    --help                   display this message and exit\n\
    --hold                   wait until a debugger will attach\n\
    --install-partition=PAR  specify stage2 install_partition [default=0x%x]\n\
    --no-config-file         do not use the config file\n\
    --no-curses              do not use curses\n\
    --read-only              do not write anything to devices\n\
    --verbose                print verbose messages\n\
    --version                print version information and exit\n\
\n\
Report bugs to bug-grub@gnu.org\n\
",
	    default_boot_drive, default_config_file,
	    default_install_partition);

  exit (status);
}


int
main (int argc, char **argv)
{
  int c;
  int hold = 0;

  /* First of all, call sync so that all in-core data is scheduled to be
     actually written to disks. This is very important because GRUB does
     not use ordinary stdio interface but raw devices.  */
  sync ();
  
  program_name = argv[0];
  default_boot_drive = boot_drive;
  default_install_partition = install_partition;
  if (config_file)
    default_config_file = config_file;
  else
    default_config_file = "NONE";

  /* Parse command-line options. */
  do
    {
      c = getopt_long (argc, argv, OPTSTRING, longopts, 0);
      switch (c)
	{
	case EOF:
	  /* Fall through the bottom of the loop. */
	  break;

	case OPT_HELP:
	  usage (0);
	  break;

	case OPT_VERSION:
	  printf ("GNU GRUB " VERSION "\n");
	  exit (0);
	  break;

	case OPT_HOLD:
	  hold = 1;
	  break;

	case OPT_CONFIG_FILE:
	  strncpy (config_file, optarg, 127); /* FIXME: arbitrary */
	  config_file[127] = '\0';
	  break;

	case OPT_INSTALL_PARTITION:
	  install_partition = strtoul (optarg, 0, 0);
	  if (install_partition == ULONG_MAX)
	    {
	      perror ("strtoul");
	      exit (1);
	    }
	  break;

	case OPT_BOOT_DRIVE:
	  boot_drive = strtoul (optarg, 0, 0);
	  if (boot_drive == ULONG_MAX)
	    {
	      perror ("strtoul");
	      exit (1);
	    }
	  break;

	case OPT_NO_CONFIG_FILE:
	  use_config_file = 0;
	  break;

	case OPT_NO_CURSES:
	  use_curses = 0;
	  break;

	case OPT_BATCH:
	  /* This is the same as "--no-config-file --no-curses".  */
	  use_config_file = 0;
	  use_curses = 0;
	  break;

	case OPT_READ_ONLY:
	  read_only = 1;
	  break;

	case OPT_VERBOSE:
	  verbose = 1;
	  break;
	  
	default:
	  usage (1);
	}
    }
  while (c != EOF);

  /* Wait until the HOLD variable is cleared by an attached debugger. */
  if (hold && verbose)
    printf ("Run \"gdb %s %d\", and set HOLD to zero.\n",
	    program_name, (int) getpid ());
  while (hold)
    sleep (1);

  /* Transfer control to the stage2 simulator. */
  exit (grub_stage2 ());
}
