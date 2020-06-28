#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
gi.require_version('Vte', '2.91')
import config
from gi.repository import GLib, Vte, Gtk, Gdk
import os
import sys
import screensize

class Terminal:

  def __init__(self):    
    self.options = {}        
    self.notebook = Gtk.Notebook()
    self.notebook.set_name("terminalpage")

  def configure(self, options):
    if options != None:
      self.options = options
    else:
      raise ValueError("Cannot configure a VTETerminal with NoneType as the options.")

  def create_terminal(self):
    # To add all widgets
    main_box = Gtk.VBox()
    main_box.set_name("boxterminal")

    terminal = Vte.Terminal()  

    self.configure(
        {
           "shell": config.shell,
           "fallback_shell": config.fallback_shell,
           "working_directory": config.working_directory,
           "audible_bell": config.audible_bell
        })

    terminal.spawn_sync(
      Vte.PtyFlags.DEFAULT, self.options["working_directory"],
      [self.options["shell"]], [],
      GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None,
    )

    screen_width, screen_height = screensize.get_screen_size() 

    # Notebook tab label
    box_tab = Gtk.HBox(spacing=8)
    box_tab.set_name("booktab")
    label_title = Gtk.Label()
    label_title.set_text(self.options["shell"])
    box_tab.pack_start(label_title, False, False, 0)
    box_tab.show_all()

    # tool box for adding new tab and for exit app buttons
    tool_box = Gtk.HBox(spacing=30)

    event_plus = Gtk.EventBox() # Tool box add button        
    event_plus.connect("enter-notify-event", self.on_mouse_enter_button_icon)
    event_plus.connect("leave-notify-event", self.on_mouse_leave_button_icon)
    event_plus.connect("button_press_event", self.create_page)
    event_plus.set_tooltip_text("Open a new tab")
    image_plus = Gtk.Image()
    image_plus.set_from_file("./icons/icon-plus.png")
    event_plus.add(image_plus)

    event_exit = Gtk.EventBox() #  Tool box exit button        
    event_exit.connect("enter-notify-event", self.on_mouse_enter_button_icon)
    event_exit.connect("leave-notify-event", self.on_mouse_leave_button_icon)
    event_exit.set_tooltip_text("Exit application")
    image_exit = Gtk.Image()
    image_exit.set_from_file("./icons/icon-exit.png")
    event_exit.add(image_exit)

    tool_box.add(event_plus)
    tool_box.add(event_exit)

    main_box.add(tool_box)
    main_box.add(terminal)
    main_box.show_all()
    main_box.set_size_request(screen_width/2, screen_height*0.5)   

    self.notebook.append_page(main_box, box_tab)    
    self.notebook.show_all 

    self.notebook.set_current_page(0)

    return self.notebook, event_exit

  def create_page(self, widget, event):
    
    main_box = Gtk.VBox()
    main_box.set_name("boxterminal")
    terminal = Vte.Terminal()

    self.configure(
        {
           "shell": config.shell,
           "fallback_shell": config.fallback_shell,
           "working_directory": config.working_directory,
           "audible_bell": config.audible_bell
        })

    terminal.spawn_sync(
      Vte.PtyFlags.DEFAULT, self.options["working_directory"],
      [self.options["shell"]], [],
      GLib.SpawnFlags.DO_NOT_REAP_CHILD, None, None,
    )

    screen_width, screen_height = screensize.get_screen_size() 

    app_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    box_tab = Gtk.HBox(spacing=8) # Box for notebook tab label and for tab close button
    close_image = Gtk.Image() # Tab close image 
    close_image.set_from_file(app_path + "/icons/icon-close.png")
    eventbox_close = Gtk.EventBox() # For close image event
    eventbox_close.set_name("eventboxclose")
    eventbox_close.add(close_image)
    eventbox_close.connect("enter-notify-event", self.on_mouse_enter_button_icon)
    eventbox_close.connect("leave-notify-event", self.on_mouse_leave_button_icon)
    eventbox_close.connect("button_press_event", self.close_tab) 
    label_title = Gtk.Label()
    label_title.set_text(self.options["shell"])

    box_tab.pack_start(label_title, False, False, 0)
    box_tab.pack_start(eventbox_close, False, False, 0)
    box_tab.set_name("booktab")  
    box_tab.show_all()

    tool_box = Gtk.HBox(spacing=30)

    event_plus = Gtk.EventBox() # notebook tab add button        
    event_plus.connect("enter-notify-event", self.on_mouse_enter_button_icon)
    event_plus.connect("leave-notify-event", self.on_mouse_leave_button_icon)
    event_plus.connect("button_press_event", self.create_page)
    event_plus.set_tooltip_text("Open a new tab")
    image_plus = Gtk.Image()
    image_plus.set_from_file("./icons/icon-plus.png")
    event_plus.add(image_plus) 

    tool_box.add(event_plus)

    main_box.add(tool_box)
    main_box.add(terminal)
    main_box.set_size_request(screen_width/2, screen_height*0.5) 
    main_box.show_all()

    self.notebook.append_page(main_box, box_tab)
    self.notebook.set_current_page(self.notebook.get_n_pages() - 1)
    self.notebook.show_all()       

  def close_tab(self, widget, event):
        if self.notebook.get_current_page() != 0:
            page = self.notebook.get_current_page()
            self.notebook.remove_page(page)

  def on_mouse_enter_button_icon(self, w, e):
    w.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
    w.get_style_context().add_class("refresh-button-hover")

  def on_mouse_leave_button_icon(self, w, e):
    w.get_window().set_cursor(None)
    w.get_style_context().remove_class("refresh-button-hover")
  