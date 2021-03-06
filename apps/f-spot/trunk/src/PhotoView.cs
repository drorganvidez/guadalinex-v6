/*
 * FSpot.PhotoView.cs
 *
 * Author(s)
 * 	Ettore Perazzoli
 * 	Larry Ewing
 *	Stephane Delcroix
 *
 * This is free software. See COPYING for details.
 */

using Gdk;
using GLib;
using Gtk;
using GtkSharp;
using System;
using System.IO;
using System.Collections.Generic;
using System.Xml.Serialization;
using Mono.Unix;

using FSpot.Xmp;
using FSpot.Widgets;
using FSpot.Utils;
using FSpot.UI.Dialog;

namespace FSpot {
	public class PhotoView : EventBox {
		FSpot.Delay commit_delay; 
	
		private bool has_selection = false;
		private FSpot.PhotoImageView photo_view;
		private ScrolledWindow photo_view_scrolled;
		private EventBox background;
		
		private Filmstrip filmstrip;
	
		private Widgets.TagView tag_view;
		
		private Entry description_entry;
		private Widgets.Rating rating;
	
		private uint restore_scrollbars_idle_id;
	
		// Public events.
	
		public delegate void PhotoChangedHandler (PhotoView me);
		public event PhotoChangedHandler PhotoChanged;
	
		public delegate void UpdateStartedHandler (PhotoView view);
		public event UpdateStartedHandler UpdateStarted;
	
		public delegate void UpdateFinishedHandler (PhotoView view);
		public event UpdateFinishedHandler UpdateFinished;

		public delegate void DoubleClickedHandler (Widget widget, BrowsableEventArgs args);
		public event DoubleClickedHandler DoubleClicked;
	
		public FSpot.PhotoImageView View {
			get { return photo_view; }
		}
	
		new public FSpot.BrowsablePointer Item {
			get { return photo_view.Item; }
		}
	
		private IBrowsableCollection query;
		public IBrowsableCollection Query {
			get { return query; }
			set { query = value; }
		}
	
		public double Zoom {
			get { return photo_view.Zoom; }
			set { photo_view.Zoom = value; }
		}
		
		public double NormalizedZoom {
			get { return photo_view.NormalizedZoom; }
			set { photo_view.NormalizedZoom = value; }
		}
	
		public void Reload ()
		{
			photo_view.Reload ();
		}
	
		private void UpdateDescriptionEntry ()
		{
			description_entry.Changed -= HandleDescriptionChanged;
			if (Item.IsValid) {
				if (description_entry.Sensitive == false)
					description_entry.Sensitive = true;
	
				string desc = Item.Current.Description;
				if (description_entry.Text != desc) {
					description_entry.Text = desc == null ? String.Empty : desc;
				}
			} else {
				description_entry.Sensitive = false;
				description_entry.Text = String.Empty;
			}
	
			tips.SetTip (description_entry, description_entry.Text ?? String.Empty, description_entry.Text ?? String.Empty);
	
			description_entry.Changed += HandleDescriptionChanged;
		}    
	
		public void UpdateRating ()
		{
			if (Item.IsValid)
				UpdateRating ((int)Item.Current.Rating);
		}

		public void UpdateRating (int r)
		{
			rating.Changed -= HandleRatingChanged;
			rating.Value = r;
			rating.Changed += HandleRatingChanged;
		}
	
		private void Update ()
		{
			if (UpdateStarted != null)
				UpdateStarted (this);
	
			UpdateDescriptionEntry ();
			UpdateRating ();

			if (UpdateFinished != null)
				UpdateFinished (this);
		}
	
		public void ZoomIn ()
		{
			photo_view.ZoomIn ();
		}
		
		public void ZoomOut ()
		{
			photo_view.ZoomOut ();
		}
	
		// Event handlers.
		private void HandleButtonPressEvent (object sender, ButtonPressEventArgs args)
		{
			if (args.Event.Type == EventType.TwoButtonPress && args.Event.Button == 1 && DoubleClicked != null)
				DoubleClicked (this, null);
			if (args.Event.Type == EventType.ButtonPress
			    && args.Event.Button == 3) {
				PhotoPopup popup = new PhotoPopup ();
				popup.Activate (this.Toplevel, args.Event);
			}
		}
	
		protected override bool OnPopupMenu ()
		{
			PhotoPopup popup = new PhotoPopup ();
			popup.Activate (this.Toplevel);
			return true;
		}
	
		private void ShowError (System.Exception e, Photo photo)
		{
			string msg = Catalog.GetString ("Error editing photo");
			string desc = String.Format (Catalog.GetString ("Received exception \"{0}\". Unable to save photo {1}"),
						     e.Message, photo.Name);
			
			HigMessageDialog md = new HigMessageDialog ((Gtk.Window)this.Toplevel, DialogFlags.DestroyWithParent, 
								    Gtk.MessageType.Error, ButtonsType.Ok, 
								    msg,
								    desc);
			md.Run ();
			md.Destroy ();
		}
	
		int changed_photo;
		private bool CommitPendingChanges ()
		{
			if (commit_delay.IsPending) {
				commit_delay.Stop ();
				((PhotoQuery)query).Commit (changed_photo);
			}
			return true;
		}
	
		private void HandleDescriptionChanged (object sender, EventArgs args) 
		{
			if (!Item.IsValid)
				return;
			
			((Photo)Item.Current).Description = description_entry.Text;
			
			if (commit_delay.IsPending)
				if (changed_photo == Item.Index)
					commit_delay.Stop ();
				else
					CommitPendingChanges ();
			
			tips.SetTip (description_entry, description_entry.Text, "This is a tip");
			changed_photo = Item.Index;
			commit_delay.Start ();
		}
	
		private void HandleRatingChanged (object o, EventArgs e)
		{
			if (!Item.IsValid)
				return;
	
			((Photo)Item.Current).Rating = (uint)(o as Widgets.Rating).Value;
	
			if (commit_delay.IsPending)
				if (changed_photo == Item.Index)
					commit_delay.Stop();
				else
					CommitPendingChanges ();
			changed_photo = Item.Index;
			commit_delay.Start ();
	 	}
	
		private void HandlePhotoChanged (FSpot.PhotoImageView view)
		{
			if (query is PhotoQuery) {
				CommitPendingChanges ();
			}
			
			tag_view.Current = Item.Current;
			Update ();
	
			if (this.PhotoChanged != null)
				PhotoChanged (this);
		}
	
		private void HandleDestroy (object sender, System.EventArgs args)
		{
			CommitPendingChanges ();
			Dispose ();
		}
	
		public bool FilmStripVisibility {
			get { return filmstrip.Visible; }
			set { filmstrip.Visible = value; }
		}
	
		Gtk.Tooltips tips = new Gtk.Tooltips ();
	
		public PhotoView (IBrowsableCollection query)
			: base ()
		{
			this.query = query;
	
			commit_delay = new FSpot.Delay (1000, new GLib.IdleHandler (CommitPendingChanges));
			this.Destroyed += HandleDestroy;
	
			Name = "ImageContainer";
			Box vbox = new VBox (false, 6);
			Add (vbox);
	
		        background = new EventBox ();
			Frame frame = new Frame ();
			background.Add (frame);
	
			frame.ShadowType = ShadowType.In;
			vbox.PackStart (background, true, true, 0);
			
			Box inner_vbox = new VBox (false , 2);
	
			frame.Add (inner_vbox);
			
			BrowsablePointer bp = new BrowsablePointer (query, -1);
			photo_view = new FSpot.PhotoImageView (bp);
	
			filmstrip = new Filmstrip (bp);
			Gdk.Pixbuf bg = new Gdk.Pixbuf (Gdk.Colorspace.Rgb, true, 8, 1, 69);
			bg.Fill (0x00000000);
			filmstrip.BackgroundTile = bg;
			filmstrip.ThumbOffset = 1;
			filmstrip.Spacing = 4;
			inner_vbox.PackStart (filmstrip, false, false, 0);
	
			photo_view.PhotoChanged += HandlePhotoChanged;
	
			photo_view_scrolled = new ScrolledWindow (null, null);

			photo_view_scrolled.SetPolicy (PolicyType.Automatic, PolicyType.Automatic);
			photo_view_scrolled.ShadowType = ShadowType.None;
			photo_view_scrolled.Add (photo_view);
			photo_view_scrolled.Child.ButtonPressEvent += HandleButtonPressEvent;
			photo_view.AddEvents ((int) EventMask.KeyPressMask);
			inner_vbox.PackStart (photo_view_scrolled, true, true, 0);
			
			HBox inner_hbox = new HBox (false, 2);
			//inner_hbox.BorderWidth = 6;
	
			tag_view = new Widgets.TagView (MainWindow.ToolTips);
			inner_hbox.PackStart (tag_view, false, true, 0);
	
			Label comment = new Label (Catalog.GetString ("Comment:"));
			inner_hbox.PackStart (comment, false, false, 0);
			description_entry = new Entry ();
			inner_hbox.PackStart (description_entry, true, true, 0);
			description_entry.Changed += HandleDescriptionChanged;
	
			rating = new Widgets.Rating();
			inner_hbox.PackStart (rating, false, false, 0);
			rating.Changed += HandleRatingChanged;
	
			SetColors ();
			
			inner_vbox.PackStart (inner_hbox, false, true, 0);
	
			vbox.ShowAll ();
	
			Realized += delegate (object o, EventArgs e) {SetColors ();};
		}

		~PhotoView ()
		{
			FSpot.Utils.Log.DebugFormat ("Finalizer called on {0}. Should be Disposed", GetType ());		
			Dispose (false);	
		}

		public override void Dispose ()
		{
			Dispose (true);
			base.Dispose ();
			System.GC.SuppressFinalize (this);
		}
	
		bool is_disposed = false;
		protected virtual void Dispose (bool disposing)
		{
			if (is_disposed)
				return;
			if (disposing) { //Free managed resources
				filmstrip.Dispose ();	
			}

			is_disposed = true;
		}

		private void SetColors ()
		{
			GtkUtil.ModifyColors (filmstrip);
			GtkUtil.ModifyColors (tag_view);
			GtkUtil.ModifyColors (photo_view);
			GtkUtil.ModifyColors (background);
			GtkUtil.ModifyColors (photo_view_scrolled);
			GtkUtil.ModifyColors (rating);
		}
	
		protected override void OnStyleSet (Style previous)
		{
			SetColors ();
		}
	}
}
