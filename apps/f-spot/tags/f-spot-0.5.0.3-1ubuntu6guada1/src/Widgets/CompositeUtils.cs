using System;
using System.Runtime.InteropServices;
using Gdk;
using Gtk;
using FSpot.Utils;

namespace FSpot.Widgets {
	public class CompositeUtils {
		[DllImport("libgdk-2.0-0.dll")]
	        static extern bool gdk_screen_is_composited (IntPtr screen);
		
		[DllImport("libgdk-2.0-0.dll")]
		static extern bool gdk_x11_screen_supports_net_wm_hint (IntPtr screen,
									IntPtr property);

		[DllImport("libgdk-2.0-0.dll")]
		static extern IntPtr gdk_x11_get_xatom_by_name_for_display (IntPtr display, string name);

		[DllImport("libgdk-2.0-0.dll")]
		static extern IntPtr gdk_screen_get_rgba_colormap (IntPtr screen);

		[DllImport("libgdk-2.0-0.dll")]
		static extern IntPtr gdk_screen_get_rgba_visual (IntPtr screen);

		[DllImport ("libgtk-win32-2.0-0.dll")]
		static extern void gtk_widget_input_shape_combine_mask (IntPtr raw, IntPtr shape_mask, int offset_x, int offset_y);

		[DllImport("libgdk-2.0-0.dll")]
		static extern void gdk_property_change(IntPtr window, IntPtr property, IntPtr type, int format, int mode, uint [] data, int nelements);

		[DllImport("libgdk-2.0-0.dll")]
		static extern void gdk_property_change(IntPtr window, IntPtr property, IntPtr type, int format, int mode, byte [] data, int nelements);
		
		public static Colormap GetRgbaColormap (Screen screen)
		{
			try {
				IntPtr raw_ret = gdk_screen_get_rgba_colormap (screen.Handle);
				Gdk.Colormap ret = GLib.Object.GetObject(raw_ret) as Gdk.Colormap;
				return ret;
			} catch {
				Gdk.Visual visual = Gdk.Visual.GetBestWithDepth (32);
				if (visual != null) {
					Gdk.Colormap cmap = new Gdk.Colormap (visual, false);
					System.Console.WriteLine ("fallback");
					return cmap;
				}
			}
			return null;
		}

		public static void  ChangeProperty (Gdk.Window win, Atom property, Atom type, PropMode mode, uint [] data)
		{
			gdk_property_change (win.Handle, property.Handle, type.Handle, 32, (int)mode,  data, data.Length * 4);
		}

		public static void  ChangeProperty (Gdk.Window win, Atom property, Atom type, PropMode mode, byte [] data)
		{
			gdk_property_change (win.Handle, property.Handle, type.Handle, 8, (int)mode,  data, data.Length);
		}

		public static bool SupportsHint (Screen screen, string name)
		{
			try {
				Atom atom = Atom.Intern (name, false);
				return gdk_x11_screen_supports_net_wm_hint (screen.Handle, atom.Handle);
			} catch {
				
				return false;
			}
		}

		public static bool SetRgbaColormap (Widget w)
		{
			Gdk.Colormap cmap = GetRgbaColormap (w.Screen);

			if (cmap != null) {
				w.Colormap = cmap;
				return true;
			}

			return false;
		}


		public static Visual GetRgbaVisual (Screen screen)
		{
			try {
				IntPtr raw_ret = gdk_screen_get_rgba_visual (screen.Handle);
				Gdk.Visual ret = GLib.Object.GetObject(raw_ret) as Gdk.Visual;
				return ret;
			} catch {
				Gdk.Visual visual = Gdk.Visual.GetBestWithDepth (32);
				if (visual != null) {
					return visual;
				}
			}
			return null;
		}

		public static bool IsComposited (Screen screen) {
			bool composited;
			try {
				composited = gdk_screen_is_composited (screen.Handle);
			} catch (EntryPointNotFoundException) {
				System.Console.WriteLine ("query composite manager locally");
				Atom atom = Atom.Intern (String.Format ("_NET_WM_CM_S{0}", screen.Number), false);
				composited = Gdk.Selection.OwnerGetForDisplay (screen.Display, atom) != null;
			}

			// FIXME check for WINDOW_OPACITY so that we support compositing on older composite manager
			// versions before they started supporting the real check given above
			if (!composited)
				composited = CompositeUtils.SupportsHint (screen, "_NET_WM_WINDOW_OPACITY");

			return composited;
		}

		public static void InputShapeCombineMask (Widget w, Pixmap shape_mask, int offset_x, int offset_y)
		{
			gtk_widget_input_shape_combine_mask (w.Handle, shape_mask == null ? IntPtr.Zero : shape_mask.Handle, offset_x, offset_y);
		}

		[DllImport("libXcomposite.dll")]
		static extern void XCompositeRedirectWindow (IntPtr display, uint window, CompositeRedirect update);

		public enum CompositeRedirect {
			Automatic = 0,
			Manual = 1
		};

		public static void RedirectDrawable (Drawable d)
		{
			uint xid = GdkUtils.GetXid (d);
			Console.WriteLine ("xid = {0} d.handle = {1}, d.Display.Handle = {2}", xid, d.Handle, d.Display.Handle);
			XCompositeRedirectWindow (GdkUtils.GetXDisplay (d.Display), GdkUtils.GetXid (d), CompositeRedirect.Manual);
		}

		public static void SetWinOpacity (Gtk.Window win, double opacity)
		{
			CompositeUtils.ChangeProperty (win.GdkWindow, 
						       Atom.Intern ("_NET_WM_WINDOW_OPACITY", false),
						       Atom.Intern ("CARDINAL", false),
						       PropMode.Replace,
						       new uint [] { (uint) (0xffffffff * opacity) });
		}

		public static Cms.Profile GetScreenProfile (Screen screen)
		{
			Atom atype;
			int  aformat;
			int  alength;
			byte [] data;

			if (Gdk.Property.Get (screen.RootWindow,
					      Atom.Intern ("_ICC_PROFILE", false),
					      Atom.Intern ("CARDINAL", false),
					      0,
					      Int32.MaxValue,
					      0, // FIXME in gtk# should be a bool
					      out atype,
					      out aformat,
					      out alength,
					      out data)) {
				return new Cms.Profile (data);
			}
			
			return null;
		}

		public static void SetScreenProfile (Screen screen, Cms.Profile profile)
		{
			byte [] data = profile.Save ();
			ChangeProperty (screen.RootWindow,
					Atom.Intern ("_ICC_PROFILE", false),
					Atom.Intern ("CARDINAL", false),
					PropMode.Replace,
					data);
		}
	}
}
