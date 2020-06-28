import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gdk, Gtk

def get_screen_size():
    w = Gtk.Window()
    s = w.get_screen()
    m = s.get_monitor_at_window(s.get_active_window())
    monitor = s.get_monitor_geometry(m)
    return monitor.width, monitor.height