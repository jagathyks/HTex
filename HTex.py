#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Gdk
from terminal import Terminal
from browser import Browser
from folderview import Folderview
from fileview import Fileview

class HTex(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)
        
        self.window = Gtk.Window 
        self.connect("key-press-event", self.on_window_key_press_event)
        self.connect("window-state-event", self.on_window_state_event)
        self.fullscreen()

        self.create_grid()    

    def create_grid(self):
        
        grid = Gtk.Grid()
        self.add(grid) 
        # from terminal.py class Terminal
        self.vte = Terminal()
        notebook, event_exit = self.vte.create_terminal()
        # For closing application
        event_exit.connect("button_press_event", self.app_close)        
        grid.add(notebook)

        # From browser.py class Browser
        self.webbrowser = Browser()
        # Creating fist browser page
        browser = self.webbrowser.create_browser()
        grid.attach(browser, 1, 0, 1, 1)        
        
        # From folderview.py class Folderview
        self.folder = Folderview()
        # Create Folder view HOME
        folderview = self.folder.create_foldeview()
        grid.attach_next_to(folderview, notebook, Gtk.PositionType.BOTTOM, 1, 1)

        # Filevew section
        self.file = Fileview()
        fileview = self.file.create_fileview()
        grid.attach_next_to(fileview, folderview, Gtk.PositionType.RIGHT, 1, 1)

    def app_close(self, widget, event):
        self.close()

    def fullscreen_mode(self):

        if self.__is_fullscreen:
            self.unfullscreen()
        else:
            self.fullscreen()

    def on_window_key_press_event(self, widget, event):

        key = Gdk.keyval_name(event.keyval)
        if key == "F11":
            self.fullscreen_mode()
        
        if key == "Escape":
            self.unfullscreen()

    def on_window_state_event(self, widget, event):

        self.__is_fullscreen = bool(event.new_window_state & Gdk.WindowState.FULLSCREEN)

def htexstyle():
    # Attach css file
    style_provider = Gtk.CssProvider()
    style_provider.load_from_path('./theme.css')
    Gtk.StyleContext.add_provider_for_screen(
    Gdk.Screen.get_default(),
    style_provider,
    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

    win = HTex()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()

if __name__ == "__main__":
    htexstyle()