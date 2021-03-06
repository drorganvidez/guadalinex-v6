/*
 * Widgets.EditorPage.cs
 *
 * Author(s)
 * 	Ruben Vermeersch <ruben@savanne.be>
 *
 * This is free software. See COPYING for details.
 */

using FSpot;
using FSpot.Editors;
using FSpot.UI.Dialog;
using FSpot.Utils;

using Gtk;

using Mono.Addins;
using Mono.Unix;

using System;
using System.Collections.Generic;

namespace FSpot.Widgets {
	public class EditorPage : SidebarPage {
		internal bool InPhotoView;
		private readonly EditorPageWidget EditorPageWidget;

		public EditorPage () : base (new EditorPageWidget (),
									   Catalog.GetString ("Edit"),
									   "mode-image-edit") {
			// TODO: Somebody might need to change the icon to something more suitable.
			// FIXME: The icon isn't shown in the menu, are we missing a size?
			EditorPageWidget = SidebarWidget as EditorPageWidget;
			EditorPageWidget.Page = this;
		}

		protected override void AddedToSidebar () {
			Sidebar.SelectionChanged += delegate (IBrowsableCollection collection) { EditorPageWidget.ShowTools (); };
			Sidebar.ContextChanged += HandleContextChanged;
		}

		private void HandleContextChanged (object sender, EventArgs args)
		{
			InPhotoView = (Sidebar.Context == ViewContext.Edit);
			EditorPageWidget.ChangeButtonVisibility ();
		}
	}

	public class EditorPageWidget : ScrolledWindow {
		private VBox widgets;
		private VButtonBox buttons;
		private Widget active_editor;

		private List<Editor> editors;
		private Editor current_editor;

		// Used to make buttons insensitive when selecting multiple images.
		private Dictionary<Editor, Button> editor_buttons;

		private EditorPage page;
		internal EditorPage Page {
			get { return page; }
			set { page = value; ChangeButtonVisibility (); }
		}

		public EditorPageWidget () {
			editors = new List<Editor> ();
			editor_buttons = new Dictionary<Editor, Button> ();
			ShowTools ();
			AddinManager.AddExtensionNodeHandler ("/FSpot/Editors", OnExtensionChanged);

		}

		private void OnExtensionChanged (object s, ExtensionNodeEventArgs args) {
			// FIXME: We do not do run-time removal of editors yet!
			if (args.Change == ExtensionChange.Add) {
				Editor editor = (args.ExtensionNode as EditorNode).GetEditor ();
				editor.ProcessingStarted += OnProcessingStarted;
				editor.ProcessingStep += OnProcessingStep;
				editor.ProcessingFinished += OnProcessingFinished;
				editors.Add (editor);
				PackButton (editor);
			}
		}

		private ProgressDialog progress;

		private void OnProcessingStarted (string name, int count) {
			progress = new ProgressDialog (name, ProgressDialog.CancelButtonType.None, count, MainWindow.Toplevel.Window);
		}

		private void OnProcessingStep (int done) {
			if (progress != null)
				progress.Update (String.Empty);
		}

		private void OnProcessingFinished () {
			if (progress != null) {
				progress.Destroy ();
				progress = null;
			}
		}

		internal void ChangeButtonVisibility () {
			foreach (Editor editor in editors) {
				Button button;
				if (editor_buttons.TryGetValue (editor, out button))
					button.Visible = Page.InPhotoView || editor.CanHandleMultiple;
			}
		}

		void PackButton (Editor editor)
		{
			Button button = new Button (editor.Label);
			if (editor.IconName != null)
				button.Image = new Image (GtkUtil.TryLoadIcon (FSpot.Global.IconTheme, editor.IconName, 22, (Gtk.IconLookupFlags)0));
			button.Clicked += delegate (object o, EventArgs e) { ChooseEditor (editor); };
			button.Show ();
			buttons.Add (button);
			editor_buttons.Add (editor, button);
		}

		public void ShowTools () {
			// Remove any open editor, if present.
			if (current_editor != null) {
				active_editor.Hide ();
				widgets.Remove (active_editor);
				active_editor = null;
				current_editor.Restore ();
				current_editor = null;
			}

			// No need to build the widget twice.
			if (buttons != null) {
				buttons.Show ();
				return;
			}

			if (widgets == null) {
				widgets = new VBox (false, 0);
				widgets.NoShowAll = true;
				widgets.Show ();
				Viewport widgets_port = new Viewport ();
				widgets_port.Add (widgets);
				Add (widgets_port);
				widgets_port.ShowAll ();
			}

			// Build the widget (first time we call this method).
			buttons = new VButtonBox ();
			buttons.BorderWidth = 5;
			buttons.Spacing = 5;
			buttons.LayoutStyle = ButtonBoxStyle.Start;

			foreach (Editor editor in editors) 
				PackButton (editor);

			buttons.Show ();
			widgets.Add (buttons);
		}

		private void ChooseEditor (Editor editor) {
			SetupEditor (editor);

			if (!editor.CanBeApplied || editor.HasSettings)
				ShowEditor (editor);
			else
				Apply (editor); // Instant apply
		}

		private bool SetupEditor (Editor editor) {
			EditorState state = editor.CreateState ();

			EditorSelection selection = new EditorSelection ();
			PhotoImageView photo_view = MainWindow.Toplevel.PhotoView.View;

			if (Page.InPhotoView && photo_view != null) {
				if (photo_view.GetSelection (out selection.x, out selection.y,
							out selection.width, out selection.height))
					state.Selection = selection;
				else
					state.Selection = null;
				state.PhotoImageView = photo_view;
			} else {
				state.Selection = null;
				state.PhotoImageView = null;
			}
			if (Page.Sidebar.Selection == null)
				return false;
			state.Items = Page.Sidebar.Selection.Items;

			editor.Initialize (state);
			return true;
		}

		private void Apply (Editor editor) {
			if (!SetupEditor (editor))
				return;

			if (!editor.CanBeApplied) {
				string msg = Catalog.GetString ("No selection available");
				string desc = Catalog.GetString ("This tool requires an active selection. Please select a region of the photo and try the operation again");

				HigMessageDialog md = new HigMessageDialog (MainWindow.Toplevel.Window,
										DialogFlags.DestroyWithParent,
										Gtk.MessageType.Error, ButtonsType.Ok,
										msg,
										desc);

				md.Run ();
				md.Destroy ();
				return;
			}

			// TODO: Might need to do some nicer things for multiple selections (progress?)
			try {
				editor.Apply ();
			} catch (Exception e) {
				string msg = Catalog.GetPluralString ("Error saving adjusted photo", "Error saving adjusted photos", 
									editor.State.Items.Length);
				string desc = String.Format (Catalog.GetString ("Received exception \"{0}\". Note that you have to develop RAW files into JPEG before you can edit them."),
							     e.Message);

				HigMessageDialog md = new HigMessageDialog (MainWindow.Toplevel.Window,
									    DialogFlags.DestroyWithParent,
									    Gtk.MessageType.Error, ButtonsType.Ok,
									    msg,
									    desc);
				md.Run ();
				md.Destroy ();
			}
			ShowTools ();
		}

		private void ShowEditor (Editor editor) {
			SetupEditor (editor);
			current_editor = editor;

			buttons.Hide ();

			// Top label
			VBox vbox = new VBox (false, 4);
			Label label = new Label ();
			label.Markup = String.Format("<big><b>{0}</b></big>", editor.Label);
			vbox.PackStart (label, false, false, 5);

			// Optional config widget
			Widget config = editor.ConfigurationWidget ();
			if (config != null) {
				vbox.PackStart (config, false, false, 0);
			}

			// Apply / Cancel buttons
			HButtonBox tool_buttons = new HButtonBox ();
			tool_buttons.LayoutStyle = ButtonBoxStyle.End;
			tool_buttons.Spacing = 5;
			tool_buttons.BorderWidth = 5;
			tool_buttons.Homogeneous = false;

			Button cancel = new Button (Stock.Cancel);
			cancel.Clicked += HandleCancel;
			tool_buttons.Add (cancel);

			Button apply = new Button (editor.ApplyLabel);
			apply.Image = new Image (GtkUtil.TryLoadIcon (FSpot.Global.IconTheme, editor.IconName, 22, (Gtk.IconLookupFlags)0));
			apply.Clicked += delegate { Apply (editor); };
			tool_buttons.Add (apply);

			// Pack it all together
			vbox.PackEnd (tool_buttons, false, false, 0);
			active_editor = vbox;
			widgets.Add (active_editor);
			active_editor.ShowAll ();
		}

		void HandleCancel (object sender, System.EventArgs args) {
			ShowTools ();
		}
	}
}
