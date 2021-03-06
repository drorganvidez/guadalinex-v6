#    Back In Time
#    Copyright (C) 2008 Oprea Dan
#
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
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import os
import os.path
import stat
import sys

if len( os.getenv( 'DISPLAY', '' ) ) == 0:
	os.putenv( 'DISPLAY', ':0.0' )

import pygtk
pygtk.require("2.0")
import gtk
import threading
import gobject
import gtk.glade
import gnomevfs
import datetime
import gettext

import config
import backup
import settingsdialog


_=gettext.gettext


class AboutDialog:
	def __init__( self, config, glade ):
		self.glade = glade 
		self.dialog = self.glade.get_widget( 'AboutDialog' )
		self.dialog.set_name( config.APP_NAME )
		self.dialog.set_version( config.VERSION )
		self.dialog.set_copyright( 'Copyright (C) 2008 Oprea Dan' )
		self.dialog.set_website( 'http://www.le-web.org/back-in-time/' )
		self.dialog.set_license( config.licenseText() );

		signals = { 
				'on_AboutDialog_response' : self.close,
			}

		self.glade.signal_autoconnect( signals )

	def close( self, button, response ):
		self.dialog.hide()

	def run( self ):
		return self.dialog.run()


class IconNames:
	def __init__( self ):
		self.all_icons = gtk.icon_theme_get_default().list_icons()
		self.cache = {}

	def getIcon( self, path ):
		if not os.path.exists(path):
			return gtk.STOCK_FILE
		
		#get mime type
		mime_type = gnomevfs.get_mime_type( path ).replace( '/', '-' )

		#search in the cache
		if mime_type in self.cache:
			return self.cache[mime_type]

		#print "path: " + path
		#print "mime: " + mime_type

		#try gnome mime
		items = mime_type.split('-')
		for aux in xrange(len(items)-1):
			icon_name = "gnome-mime-" + '-'.join(items[:len(items)-aux])
			if icon_name in self.all_icons:
				#print "icon: " + icon_name
				self.cache[mime_type] = icon_name
				return icon_name

		#try simple mime
		for aux in xrange(len(items)-1):
			icon_name = '-'.join(items[:len(items)-aux])
			if icon_name in self.all_icons:
				#print "icon: " + icon_name
				self.cache[mime_type] = icon_name
				return icon_name

		#try folder
		if os.path.isdir(path):
			icon_name = 'folder'
			if icon_name in self.all_icons:
				#print "icon: " + icon_name
				self.cache[mime_type] = icon_name
				return icon_name

			#print "icon: " + icon_name
			icon_name = gtk.STOCK_DIRECTORY
			self.cache[mime_type] = icon_name
			return icon_name

		#file icon
		icon_name = gtk.STOCK_FILE
		self.cache[mime_type] = icon_name
		return icon_name


class MainWindow:
	def __init__( self ):
		self.backup = backup.Backup()
		self.config = self.backup.config
		self.specialBackgroundColor = 'lightblue'

		self.glade = gtk.glade.XML( self.config.gladeFile(), None, 'backintime' )

		signals = { 
				'on_MainWindow_destroy' : gtk.main_quit,
				'on_MainWindow_delete_event' : self.on_close,
				'on_btnExit_clicked' : self.on_close,
				'on_btnAbout_clicked' : self.on_btnAbout_clicked,
				'on_btnSettings_clicked' : self.on_btnSettings_clicked,
				'on_btnBackup_clicked' : self.on_btnBackup_clicked,
				'on_btnRestore_clicked' : self.on_btnRestore_clicked,
				'on_listPlaces_cursor_changed' : self.on_listPlaces_cursor_changed,
				'on_listTimeLine_cursor_changed' : self.on_listTimeLine_cursor_changed,
				'on_btnFolderUp_clicked' : self.on_btnFodlerUp_clicked,
				'on_listFolderView_row_activated' : self.on_listFolderView_row_activated
			}

		self.glade.signal_autoconnect( signals )

		self.window = self.glade.get_widget( 'MainWindow' )
		self.window.set_title( self.config.APP_NAME )

		#icons
		self.iconNames = IconNames()

		#fix a glade bug
		self.glade.get_widget( 'btnCurrentPath' ).set_expand( True )

		#status bar
		self.statusBar = self.glade.get_widget( 'statusBar' )
		self.statusBar.push( 0, _('Done') )

		#setup places view
		self.listPlaces = self.glade.get_widget( 'listPlaces' )

		pixRenderer = gtk.CellRendererPixbuf()
		textRenderer = gtk.CellRendererText()
		
		column = gtk.TreeViewColumn( _('Places') )
		column.pack_start( pixRenderer, False )
		column.pack_end( textRenderer, True )
		column.add_attribute( pixRenderer, 'icon-name', 2 )
		column.add_attribute( textRenderer, 'markup', 0 )
		column.set_cell_data_func( pixRenderer, self.placesPixRendererFunction, None )
		column.set_cell_data_func( textRenderer, self.placesTextRendererFunction, None )
		#column.set_alignment( 0.5 )
		self.listPlaces.append_column( column )

		self.storePlaces = gtk.ListStore( str, str, str )
		self.listPlaces.set_model( self.storePlaces )
		self.listPlaces.get_selection().set_select_function( self.placesSelectFunction, self.storePlaces )

		#setup folder view
		self.listFolderView = self.glade.get_widget( 'listFolderView' )

		pixRenderer = gtk.CellRendererPixbuf()
		textRenderer = gtk.CellRendererText()

		column = gtk.TreeViewColumn( _('Name') )
		column.pack_start( pixRenderer, False )
		column.pack_end( textRenderer, True )
		#column.add_attribute( pixRenderer, 'stock-id', 2 )
		column.add_attribute( pixRenderer, 'icon-name', 2 )
		column.add_attribute( textRenderer, 'markup', 0 )
		column.set_expand( True )
		column.set_sizing( gtk.TREE_VIEW_COLUMN_AUTOSIZE )
		#column.set_alignment( 0.5 )
		#self.lblTime = gtk.Label()
		#self.lblTime.set_markup( "<b>%s</b>" % "Now" )
		#self.lblTime.show()
		#column.set_widget( self.lblTime )
		self.listFolderView.append_column( column )

		textRenderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn( _('Size') )
		column.pack_end( textRenderer, True )
		column.add_attribute( textRenderer, 'markup', 4 )
		#column.set_alignment( 0.5 )
		self.listFolderView.append_column( column )

		textRenderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn( _('Date') )
		column.pack_end( textRenderer, True )
		column.add_attribute( textRenderer, 'markup', 5 )
		#column.set_alignment( 0.5 )
		self.listFolderView.append_column( column )

		self.storeFolderView = gtk.ListStore( str, str, str, int, str, str )
		self.listFolderView.set_model( self.storeFolderView )

		#setup timeline view
		self.listTimeLine = self.glade.get_widget( 'listTimeLine' )

		textRenderer = gtk.CellRendererText()

		column = gtk.TreeViewColumn( _('Timeline'), textRenderer, markup = 0 )
		column.set_cell_data_func( textRenderer, self.placesTextRendererFunction, None )
		#column.set_alignment( 0.5 )
		self.listTimeLine.append_column( column )

		self.storeTimeLine = gtk.ListStore( str, str )
		self.listTimeLine.set_model( self.storeTimeLine )
		self.listTimeLine.get_selection().set_select_function( self.placesSelectFunction, self.storeTimeLine )
		self.updateTimeLine = False

		#calculate specialBackgroundColor
		style = self.listTimeLine.get_style()
		bg1 = style.bg[gtk.STATE_NORMAL]
		bg2 = style.bg[gtk.STATE_SELECTED]
		self.specialBackgroundColor = gtk.gdk.Color( (2 * bg1.red + bg2.red) / 3, (2 * bg1.green + bg2.green) / 3,(2 * bg1.blue + bg2.blue) / 3 ).to_string()

		#restore size & position
		if self.config.MAIN_WINDOW_X >= 0 and self.config.MAIN_WINDOW_Y >= 0:
			self.window.move( self.config.MAIN_WINDOW_X, self.config.MAIN_WINDOW_Y )

		if self.config.MAIN_WINDOW_WIDTH > 0 and self.config.MAIN_WINDOW_HEIGHT > 0:
			self.window.resize( self.config.MAIN_WINDOW_WIDTH, self.config.MAIN_WINDOW_HEIGHT )

		if self.config.MAIN_WINDOW_HPANED1_POSITION > 0 and self.config.MAIN_WINDOW_HPANED2_POSITION > 0:
			self.glade.get_widget('hpaned1').set_position( self.config.MAIN_WINDOW_HPANED1_POSITION )
			self.glade.get_widget('hpaned2').set_position( self.config.MAIN_WINDOW_HPANED2_POSITION )

		self.aboutDialog = AboutDialog( self.config, self.glade )
		self.settingsDialog = settingsdialog.SettingsDialog( self.config, self.glade )

		self.window.show()

		#set window handle in pid file
		file = open( self.config.pidFile(), 'at' )
		file.write( ";%s" % str(self.window.window.xid) )
		file.close()

		gobject.timeout_add( 100, self.onInit )

	def onInit( self ):
		if not self.config.isConfigured():
			self.settingsDialog.run()

			if not self.config.isConfigured():
				gtk.main_quit()
				return False

		self.updateAll( True )

		self.forceWaitLock = False
		self.updateBackupInfo()
		gobject.timeout_add( 1000, self.updateBackupInfo )
		return False

	def updateAll( self, init ):
		#fill lists
		if init:
			self.folderPath = '/'
			if len(self.config.LAST_PATH) > 0 and os.path.isdir(self.config.LAST_PATH):
				self.folderPath = self.config.LAST_PATH
		self.backupPath = '/'
		self.lastBackupList = []

		self.fillPlaces()
		self.fillTimeLine()
		self.updateFolderView( 1 )

	def placesPixRendererFunction( self, column, renderer, model, iter, user_data ):
		if len( model.get_value( iter, 2 ) ) == 0:
			renderer.set_property( 'visible', False )
		else:
			renderer.set_property( 'visible', True )

	def placesTextRendererFunction( self, column, renderer, model, iter, user_data ):
		if len( model.get_value( iter, 1 ) ) == 0:
			renderer.set_property( 'cell-background-set', True )
			renderer.set_property( 'cell-background', self.specialBackgroundColor )
		else:
			renderer.set_property( 'cell-background-set', False )

	def placesSelectFunction( self, info, store ):
		if len( store.get_value( store.get_iter( info[0] ), 1 ) ) == 0:
			return False
		return True

	def updateBackupInfo( self, forceWaitLock = False ):
		if None is self.glade.get_widget( 'btnBackup' ):
			return True

		#print "forceWaitLock: %s" % forceWaitLock

		if forceWaitLock:
			self.forceWaitLock = True
		
		busy = self.backup.isBusy()
		if busy:
			self.forceWaitLock = False

		fakeBusy = busy or self.forceWaitLock
		self.glade.get_widget( 'btnBackup' ).set_sensitive( not fakeBusy )

		if fakeBusy:
			if not self.updateTimeLine or forceWaitLock:
				self.statusBar.push( 0, _('Working ...') )
				self.updateTimeLine = True
		elif self.updateTimeLine:
			self.updateTimeLine = False
			lastBackupList = self.lastBackupList

			self.fillTimeLine()

			#print "New backup: %s" % self.lastBackupList
			#print "Last backup: %s" % lastBackupList

			if lastBackupList != self.lastBackupList:
				self.statusBar.push( 0, _('Done') )
			else:
				self.statusBar.push( 0, _('Done, no backup needed') )

		return True

	def fillPlaces( self ):
		self.storePlaces.clear()

		#add global places
		self.storePlaces.append( [ "<b>%s</b>" % _('Global'), '', '' ] )
		self.storePlaces.append( [ _('Root'), '/', gtk.STOCK_HARDDISK ] )
		self.storePlaces.append( [ _('Home'), os.path.expanduser( '~' ), gtk.STOCK_HOME ] )

		#add bookmarks
		rawbookmarks = ''
		
		try:
			file = open( os.path.expanduser('~/.gtk-bookmarks') )
			rawbookmarks = file.read()
			file.close()
		except:
			pass

		bookmarks = []
		for rawbookmark in rawbookmarks.split( '\n' ):
			if rawbookmark.startswith( 'file://' ):
				index = rawbookmark.rfind( ' ' )
				if index > 0:
					bookmarks.append( ( rawbookmark[ 7 : index ], rawbookmark[ index + 1 : ] ) )
				elif index < 0:
					index = rawbookmark.rfind( '/' )
					if index > 0:
						bookmarks.append( ( rawbookmark[ 7 : ], rawbookmark[ index + 1 : ] ) )

		if len( bookmarks ) > 0:
			self.storePlaces.append( [ "<b>%s</b>" % _('Bookmarks'), '', '' ] )
			for bookmark in bookmarks:
				self.storePlaces.append( [ bookmark[1], bookmark[0], self.iconNames.getIcon(bookmark[0]) ] )

		#add backup folders
		includeFolders = self.config.includeFolders()
		if len( includeFolders ) > 0:
			folders = includeFolders.split( ':' )
			if len( folders ) > 0:
				self.storePlaces.append( [ "<b>%s</b>" % _('Backup Directories'), '', '' ] )
				for folder in folders:
					self.storePlaces.append( [ folder, folder, gtk.STOCK_SAVE ] )

	def fillTimeLine( self ):
		currentSelection = '/'
		iter = self.listTimeLine.get_selection().get_selected()[1]
		if not iter is None:
			currentSelection = self.storeTimeLine.get_value( iter, 1 )

		self.storeTimeLine.clear()
		self.storeTimeLine.append( [ _('Now'), '/' ] )

		backupList = self.backup.getBackupList()
		#print backupList

		self.lastBackupList = backupList

		groups = []
		now = datetime.date.today()

		#today
		date = now
		groups.append( (_('Today'), self.config.backupName( date ), []) )

		#yesterday
		date = now - datetime.timedelta( days = 1 )
		groups.append( (_('Yesterday'), self.config.backupName( date ), []) )

		#this week
		date = now - datetime.timedelta( days = now.weekday() )
		groups.append( (_('This week'), self.config.backupName( date ), []) )

		#last week
		date = now - datetime.timedelta( days = now.weekday() + 7 )
		groups.append( (_('Last week'), self.config.backupName( date ), []) )

		#fill groups
		for backupDate in backupList:
			found = False

			for group in groups:
				if backupDate >= group[1]:
					group[2].append( backupDate )
					found = True
					break

			if not found:
				year = int( backupDate[ 0 : 4 ] )
				month = int( backupDate[ 4 : 6 ] )
				date = datetime.date( year, month, 1 )

				groupName = ''
				if year == now.year:
					groupName = date.strftime( '%B' ).capitalize()
				else:
					groupName = date.strftime( '%B, %Y' ).capitalize()

				groups.append( ( groupName, self.config.backupName( date ), [ backupDate ]) )

		#print 'Backup list:'
		#print backupList
		#print 'Groups:'
		#print groups

		#fill timeline list
		for group in groups:
			if len( group[2] ) > 0:
				self.storeTimeLine.append( [ "<b>%s</b>" % group[0], ''] );
				for backupDate in group[2]:
					nice_name = "%s-%s-%s %s:%s:%s" % ( backupDate[ 0 : 4 ], backupDate[ 4 : 6 ], backupDate[ 6 : 8 ], backupDate[ 9 : 11 ], backupDate[ 11 : 13 ], backupDate[ 13 : 15 ]  )
					self.storeTimeLine.append( [ nice_name, os.path.join( self.config.backupPath( backupDate ), 'backup' ) ] )

		#select previous item
		iter = self.storeTimeLine.get_iter_first()
		while not iter is None:
			if currentSelection == self.storeTimeLine.get_value( iter, 1 ):
				break
			iter = self.storeTimeLine.iter_next( iter )

		if iter is None:
			iter = self.storeTimeLine.get_iter_first()

		self.listTimeLine.get_selection().select_iter( iter )

	def on_close( self, *params ):
		self.config.MAIN_WINDOW_X, self.config.MAIN_WINDOW_Y = self.window.get_position()
		self.config.MAIN_WINDOW_WIDTH, self.config.MAIN_WINDOW_HEIGHT = self.window.get_size()
		self.config.MAIN_WINDOW_HPANED1_POSITION = self.glade.get_widget('hpaned1').get_position()
		self.config.MAIN_WINDOW_HPANED2_POSITION = self.glade.get_widget('hpaned2').get_position()
		self.config.LAST_PATH = self.folderPath 

		self.config.save()
		self.window.destroy()
		return True

	def on_listTimeLine_cursor_changed( self, list ):
		if list.get_selection().path_is_selected( list.get_cursor()[ 0 ] ):
			self.updateFolderView( 2 )

	def on_listPlaces_cursor_changed( self, list ):
		if list.get_selection().path_is_selected( list.get_cursor()[ 0 ] ):
			iter = list.get_selection().get_selected()[1]
			folderPath = self.storePlaces.get_value( iter, 1 )
			if folderPath != self.folderPath:
				self.folderPath = folderPath
				self.updateFolderView( 0 )

	def on_listFolderView_row_activated( self, list, path, column ):
		iter = list.get_selection().get_selected()[1]
		path = self.storeFolderView.get_value( iter, 1 )

		#directory
		if 0 == self.storeFolderView.get_value( iter, 3 ):
			self.folderPath = path
			self.updateFolderView( 1 )
			return

		#file
		path = os.path.join( self.backupPath, path[ 1 : ] )
		cmd = "gnome-open \"%s\"" % path
		print cmd
		os.system( cmd )


	def on_btnFodlerUp_clicked( self, button ):
		if len( self.folderPath ) <= 1:
			return

		index = self.folderPath.rfind( '/' )
		if index < 1:
			parentPath = "/"
		else:
			parentPath = self.folderPath[ : index ]

		self.folderPath = parentPath
		self.updateFolderView( 1 )

	def on_btnRestore_clicked( self, button ):
		iter = self.listFolderView.get_selection().get_selected()[1]
		if not iter is None:
			button.set_sensitive( False )
			gobject.timeout_add( 100, self.restore_ )
	
	def restore_( self ):
		iter = self.listFolderView.get_selection().get_selected()[1]
		if not iter is None:
			backupSuffix = '.backup.' + datetime.date.today().strftime( '%Y%m%d' )
			path = self.storeFolderView.get_value( iter, 1 )

			cmd = "rsync -avR --backup --suffix=%s --one-file-system --chmod=+w %s/.%s %s" % ( backupSuffix, self.backupPath, path, '/' )
			print "[restore] cmd: " + cmd
			os.system( cmd )

		self.glade.get_widget( 'btnRestore' ).set_sensitive( True )

	def on_btnAbout_clicked( self, button ):
		self.aboutDialog.run()

	def on_btnSettings_clicked( self, button, ):
		backupPath = self.config.backupBasePath()
		includeFolders = self.config.includeFolders()

		self.settingsDialog.run()

		if not self.config.isConfigured():
			gtk.main_quit()
		else:
			if backupPath != self.config.backupBasePath() or includeFolders != self.config.includeFolders():
				self.updateAll( False )

	def on_btnBackup_clicked( self, button ):
		button.set_sensitive( False )
		self.updateTimeLine = True
		
		if self.backup.isBusy():
			self.updateBackupInfo()
			return

		#backup.backup()
		app = 'backintime'
		if os.path.isfile( './backintime' ):
			app = './backintime'
		cmd = "nice -n 19 %s --backup &" % app
		os.system( cmd )

		self.updateBackupInfo( True )

	def updateFolderView( self, changedFrom ): #0 - places, 1 - folder view, 2 - timeline
		#update backup time
		if 2 == changedFrom:
			iter = self.listTimeLine.get_selection().get_selected()[1]
			backupTime = self.storeTimeLine.get_value( iter, 0 )
			self.backupPath = self.storeTimeLine.get_value( iter, 1 )
			#self.lblTime.set_markup( "<b>%s</b>" % backupTime )

		#update folderup button state
		self.glade.get_widget( 'btnFolderUp' ).set_sensitive( len( self.folderPath ) > 1 )

		#update restor button state
		self.glade.get_widget( 'btnRestore' ).set_sensitive( len( self.backupPath ) > 1 )

		#display current folder
		self.glade.get_widget( 'editCurrentPath' ).set_text( self.folderPath )

		#update selected places item
		if 1 == changedFrom:
			iter = self.storePlaces.get_iter_first()
			while not iter is None:
				placePath = self.storePlaces.get_value( iter, 1 )
				if placePath == self.folderPath:
					break
				iter = self.storePlaces.iter_next( iter )

			if iter is None:
				self.listPlaces.get_selection().unselect_all()
			else:
				self.listPlaces.get_selection().select_iter( iter )

		#update folder view
		fullPath = os.path.join( self.backupPath, self.folderPath[ 1 : ] )
		allFiles = []

		try:
			allFiles = os.listdir( fullPath )
			allFiles.sort()
		except:
			pass


		files = []
		folders = []
		for file in allFiles:
			if len( file ) == 0:
				continue
			if file[ 0 ] == '.':
				continue

			path = os.path.join( fullPath, file )

			file_size = -1
			file_date = -1

			#try:
			file_stat = os.stat( path )
			file_size = file_stat[stat.ST_SIZE]
			file_date = file_stat[stat.ST_MTIME]
			#except:
			#	pass

			#format size
			if file_size < 0:
				file_size = 'unknown'
			elif file_size < 1024:
				file_size = str( file_size ) + ' bytes'
			elif file_size < 1024 * 1024:
				file_size = file_size / 1024
				file_size = str( file_size ) + ' KB'
			elif file_size < 1024 * 1024 * 1024:
				file_size = file_size / ( 1024 * 1024 )
				file_size = str( file_size ) + ' MB'
			else:
				file_size = file_size / ( 1024 * 1024 * 1024 )
				file_size = str( file_size ) + ' GB'

			#format date
			if file_date < 0:
				file_date = 'unknown'
			else:
				file_date = datetime.datetime.fromtimestamp(file_date).isoformat(' ')

			if os.path.isdir( path ):
				folders.append( [ file, file_size, file_date, self.iconNames.getIcon(path) ] )
			else:
				files.append( [ file, file_size, file_date, self.iconNames.getIcon(path) ] )

		#try to keep old selected file
		selectedFile = ""
		iter = self.listFolderView.get_selection().get_selected()[1]
		if not iter is None:
			selectedFile = self.storeFolderView.get_value( iter, 1 )

		#populate the list
		self.storeFolderView.clear()

		selectedIter = None
		for item in folders:
			relPath = os.path.join( self.folderPath, item[0] )
			newIter = self.storeFolderView.append( [ item[0], relPath, item[3], 0, item[1], item[2] ] )
			if selectedFile == relPath:
				selectedIter = newIter 

		for item in files:
			relPath = os.path.join( self.folderPath, item[0] )
			newIter = self.storeFolderView.append( [ item[0], relPath, item[3], 1, item[1], item[2] ] )
			if selectedFile == relPath:
				selectedIter = newIter 

		#select old item or the first item
		if len( folders ) > 0 or len( files ) > 0:
			if selectedIter is None:
				selectedIter = self.storeFolderView.get_iter_first()
			self.listFolderView.get_selection().select_iter( selectedIter )


class GTKMainThread(threading.Thread): #used to display status icon
	def run(self):
		gtk.main()


def take_snapshot():
	display = gtk.gdk.display_get_default()
	statusIcon =  None

	if not display is None:
		gtk.gdk.threads_init()
		GTKMainThread().start()

		try:
			statusIcon = gtk.StatusIcon()
			statusIcon.set_from_stock( gtk.STOCK_SAVE )
			statusIcon.set_visible( True )
			statusIcon.set_tooltip(_("Back In Time: take snapshot ..."))
		except:
			pass

	backup.Backup().backup()

	if not statusIcon is None:
		statusIcon.set_visible( False )

	if not display is None:
		gtk.main_quit()


if __name__ == '__main__':
	if len( sys.argv ) > 1:
		if sys.argv[1] == '--backup':
			take_snapshot()
			sys.exit(0)

	pidFile = config.Config().pidFile()
	if os.path.isfile( pidFile ):
		pid = 0
		xid = 0

		try:
			file = open( pidFile, 'rt' )
			fields = file.read().split(';')
			file.close()
			pid = int( fields[0] )
			xid = int( fields[1] )
		except:
			pass

		if 0 != pid:
			processExists = False
			try:
				os.kill(pid,0)
				processExists = True 
			except:
				pass

			if processExists:
				if 0 != xid:
					try:
						window = gtk.gdk.window_foreign_new( xid )
						window.raise_()
					except:
						pass
				exit(0)

	file = open( pidFile, 'wt' )
	file.write( str(os.getpid()) )
	file.close()

	mainWindow = MainWindow()
	gtk.main()

	os.system( "rm %s" % pidFile )

