#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import screensize

mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
maincontainer = Gtk.Fixed()
class Fileview:

    def create_fileview(self):
        
        screen_width, screen_height = screensize.get_screen_size() 
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox.set_name("fileview")
        lblhead =Gtk.Label()
        scroll = Gtk.ScrolledWindow.new()
        scroll.set_size_request(screen_width/2, screen_height*0.4)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        mainbox.pack_start(lblhead, False, False, 0)

        image = Gtk.Image()        
        imagebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)        
        image.show_all()        
        imagebox.pack_start(image, True, True, 0)
        scroll.add(imagebox)
        mainbox.pack_start(scroll, False, False, 0)
        maincontainer.add(mainbox)
        maincontainer.show_all()
        
        return maincontainer

    def update_fileview(self, file):
        screen_width, screen_height = screensize.get_screen_size() 
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox.set_name("fileview")
        lblhead =Gtk.Label(file)
        lblhead.set_name("lblhead")
        scroll = Gtk.ScrolledWindow.new()
        scroll.set_size_request(screen_width/2, screen_height*0.4)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        mainbox.pack_start(lblhead, False, False, 0)        
        textview = Gtk.TextView()        
        textview.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0, 0, 0, 1))
        textbuffer = textview.get_buffer()
        try:
            with open(file, 'r') as fo:
                data = fo.read()
                textbuffer.set_text(data)
        except:
            lblerror = Gtk.Label("Error: File opening error")
            scroll.add(lblerror)

        scroll.add(textview)
        mainbox.pack_start(scroll, False, False, 0)
        maincontainer.add(mainbox)
        maincontainer.show_all()

            
    def update_imageview(self, path):
        screen_width, screen_height = screensize.get_screen_size() 
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox.set_name("fileview")
        lblhead =Gtk.Label(path)
        lblhead.set_name("lblhead")
        scroll = Gtk.ScrolledWindow.new()
        scroll.set_size_request(screen_width/2, screen_height*0.4)
        scroll.set_hexpand(True)
        scroll.set_vexpand(True)
        mainbox.pack_start(lblhead, False, False, 0)

        image = Gtk.Image()        
        imagebox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        image.set_from_file(path)
        image.show_all()        
        imagebox.pack_start(image, True, True, 0)
        scroll.add(imagebox)
        mainbox.pack_start(scroll, False, False, 0)
        maincontainer.add(mainbox)
        maincontainer.show_all()

    def delete_child(self):
        Gtk.Container.destroy(mainbox)


