#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
import os
import sys
from gi.repository import Pango as pango
from fileview import Fileview
import config
import imghdr
import screensize

class Folderview:
    def __init__(self):         

        self.options = {}
        self.create_foldeview()

    def configure(self, options):
        if options != None:
            self.options = options
        else:
            raise ValueError("Cannot configure folderview with NoneType as the options.")

    def create_foldeview(self): 
        
        self.configure(
        {
           "working_directory": config.working_directory
        })

        path = self.options["working_directory"]

        root_path = os.path.abspath(os.sep)        

        listoffiles = os.listdir(path)
        listoffiles.sort()
        
        col = 1
        dir_box = Gtk.VBox()
        screen_width, screen_height = screensize.get_screen_size() 
        
        maincontainer = Gtk.Fixed()
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)  
        mainbox.set_name("folderview")
        lblhead = Gtk.Label(path.replace("/", "  >  "))
        lblhead.set_name("lblhead")
        mainbox.pack_start(lblhead, False, False, 0)
        
        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(screen_width/2, screen_height*0.4)

        if path != root_path:
            rowbox = Gtk.HBox(spacing=3)
            imagebox = Gtk.VBox(spacing=4)
            dirimage = Gtk.Image()
            dirimage.set_from_file("./icons/icon-up.png")
            imagebox.pack_start(dirimage, True, True, 0)
            dirlable = Gtk.Label("Go up")
            imagebox.pack_end(dirlable, True, True, 0)
            eventbox = Gtk.EventBox()
            eventbox.add(imagebox)
            eventbox.connect("button_press_event",self.on_folder_click, path, "goup", maincontainer, mainbox)
            eventbox.connect("enter-notify-event", self.on_mouse_enter)
            eventbox.connect("leave-notify-event", self.on_mouse_leave)
            eventbox.set_tooltip_text("Go Up")
            rowbox.pack_start(eventbox, False, False, 50)            
            col = 2


        # first directories        
        for dir_entry in listoffiles:
            fullpath = os.path.join(path, dir_entry)
            if os.path.isdir(fullpath):
                if col == 1:
                    rowbox = Gtk.HBox(spacing=3)

                imagebox = Gtk.VBox(spacing=4)
                dirimage = Gtk.Image()
                dirimage.set_from_file("./icons/icon-folder.png")
                imagebox.pack_start(dirimage, True, True, 0)
                dirlable = Gtk.Label(dir_entry)
                dirlable.set_max_width_chars(5)
                dirlable.set_ellipsize(pango.EllipsizeMode.END)
                imagebox.pack_end(dirlable, True, True, 0)
                eventbox = Gtk.EventBox()
                eventbox.add(imagebox)                
                eventbox.connect("button_press_event",self.on_folder_click, fullpath, "dir", maincontainer, mainbox)
                eventbox.connect("enter-notify-event", self.on_mouse_enter)
                eventbox.connect("leave-notify-event", self.on_mouse_leave)               
                eventbox.set_tooltip_text(dir_entry)
                rowbox.pack_start(eventbox, False, False, 50)
                
                col = col + 1
                if col == 6:
                    col = 1

                dir_box.pack_start(rowbox, False, False, 0)

        for file_entry in listoffiles:
            fullpath = os.path.join(path, file_entry)
            if os.path.isdir(fullpath) == False:
                if col == 1:
                    rowbox =Gtk.HBox(spacing=3)
                
                imagebox = Gtk.VBox(spacing=4)
                fileimage = Gtk.Image()
                fileimage.set_from_file("." + self.get_file_icon(fullpath))
                imagebox.pack_start(fileimage, True, True, 0)
                filelable = Gtk.Label(file_entry)
                filelable.set_max_width_chars(5)
                filelable.set_ellipsize(pango.EllipsizeMode.END)
                imagebox.pack_end(filelable, True, True, 0)
                eventbox = Gtk.EventBox()
                eventbox.add(imagebox)
                eventbox.connect("button_press_event",self.on_folder_click, fullpath, "dir", maincontainer, mainbox)
                eventbox.connect("enter-notify-event", self.on_mouse_enter)
                eventbox.connect("leave-notify-event", self.on_mouse_leave)
                eventbox.set_tooltip_text(file_entry)
                rowbox.pack_start(eventbox, False, False, 50)

                col = col + 1
                if col == 6:
                    col = 1

                dir_box.pack_start(rowbox, False, False, 0)  

        scroll.add(dir_box)
        scroll.show_all()
        mainbox.pack_start(scroll, False, False, 0)
        maincontainer.add(mainbox)

        return maincontainer    

    def on_folder_click(self, widget, event, current_path, flag, maincontainer, child):
        
        if flag == "goup": # if goup click
            os.chdir(os.path.dirname(current_path))
            parent_folder = os.path.dirname(os.getcwd())            
            Gtk.Container.destroy(child)
            self.update_foldeview(maincontainer, parent_folder)
            
        else: # if directory or file click
            if os.path.isdir(current_path): # directory click
                # check permission
                read_write = os.access(current_path, os.R_OK)
                # if permission
                if read_write:   
                    Gtk.Container.destroy(child)
                    self.update_foldeview(maincontainer, current_path)
                else:  # if no permission
                    Gtk.Container.destroy(child)
                    self.permission_errorview(current_path, maincontainer)
            else:# file click
                if imghdr.what(current_path) == None: #if file not image
                    
                    self.file = Fileview()
                    self.file.delete_child()
                    self.file.update_fileview(current_path)

                else: # if file is image
                    self.file = Fileview()
                    self.file.delete_child()
                    self.file.update_imageview(current_path)

            
    def on_mouse_enter(self, w, e):
        w.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
        w.get_style_context().add_class("refresh-button-hover")

    def on_mouse_leave(self, w, e):
        w.get_window().set_cursor(None)
        w.get_style_context().remove_class("refresh-button-hover")


    def permission_errorview(self, current_path, maincontainer):

        app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        dir_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox.set_name("folderview")
        lblhead = Gtk.Label(current_path.replace("/", "  >  "))
        lblhead.set_name("lblhead")
        mainbox.pack_start(lblhead, False, False, 0)

        screen_width, screen_height = screensize.get_screen_size() 

        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(screen_width/2, screen_height*0.4)
        # go up box
        rowbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        imagebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        dirimage = Gtk.Image()            
        dirimage.set_from_file(app_path + "/icons/icon-up.png")
        imagebox.pack_start(dirimage, True, True, 0)
        dirlable = Gtk.Label("Go up")
        imagebox.pack_end(dirlable, True, True, 0)
        eventbox = Gtk.EventBox()
        eventbox.add(imagebox)
        eventbox.connect("button_press_event",self.on_folder_click, current_path, "goup", maincontainer, scroll)
        eventbox.connect("enter-notify-event", self.on_mouse_enter)
        eventbox.connect("leave-notify-event", self.on_mouse_leave)
        eventbox.set_tooltip_text("Go Up")
        rowbox.pack_start(eventbox, False, False, 50)
        # permission error box
        errorlable = Gtk.Label("Permission denied")
        eventbox1 = Gtk.EventBox()
        eventbox1.add(errorlable)
        eventbox1.connect("button_press_event",self.on_folder_click, current_path, "goup", maincontainer, scroll)
        eventbox1.connect("enter-notify-event", self.on_mouse_enter)
        eventbox1.connect("leave-notify-event", self.on_mouse_leave)
        eventbox1.set_tooltip_text("Go Up")
        rowbox.pack_start(eventbox1, False, False, 50)

        dir_box.pack_start(rowbox, False, False, 0)
        
        scroll.add(dir_box)
        scroll.show_all()
        mainbox.pack_start(scroll, False, False, 0)
        mainbox.show_all()
        maincontainer.add(mainbox)

    def get_file_icon(self, path):

        filename, file_extension = os.path.splitext(path)
        print(filename)

        if file_extension == ".pdf":
            icon_file = '/icons/icon-pdf.png'
        elif file_extension == ".txt":
            icon_file = "/icons/icon-txt.png"
        elif file_extension == ".xml":
            icon_file = "/icons/icon-xml.png"
        elif file_extension == ".avi":
            icon_file = "/icons/icon-avi.png"
        elif file_extension == ".cls":
            icon_file = "/icons/icon-cls.png"
        elif file_extension == ".png":
            icon_file = "/icons/icon-png.png"
        elif file_extension == ".csv":
            icon_file = "/icons/icon-csv.png"
        elif file_extension == ".dll":
            icon_file = "/icons/icon-dll.png"
        elif file_extension == ".doc":
            icon_file = "/icons/icon-doc.png"
        elif file_extension == ".exe":
            icon_file = "/icons/icon-exe.png"
        elif file_extension == ".flv":
            icon_file = "/icons/icon-flv.png"
        elif file_extension == ".gif":
            icon_file = "/icons/icon-gif.png"
        elif file_extension == ".html":
            icon_file = "/icons/icon-html.png"
        elif file_extension == ".htm":
            icon_file = "/icons/icon-htm.png"
        elif file_extension == ".jpg":
            icon_file = "/icons/icon-jpg.png"
        elif file_extension == ".mov":
            icon_file = "/icons/icon-mov.png"
        elif file_extension == ".mp3":
            icon_file = "/icons/icon-mp3.png"
        elif file_extension == ".ogg":
            icon_file = "/icons/icon-ogg.png"
        elif file_extension == ".rar":
            icon_file = "/icons/icon-rar.png"
        elif file_extension == ".tar":
            icon_file = "/icons/icon-tar.png"
        elif file_extension == ".tif":
            icon_file = "/icons/icon-tif.png"
        elif file_extension == ".ttf":
            icon_file = "/icons/icon-ttf.png"
        elif file_extension == ".wav":
            icon_file = "/icons/icon-wav.png"
        elif file_extension == ".xls":
            icon_file = "/icons/icon-xls.png"
        elif file_extension == ".zip":
            icon_file = "/icons/icon-zip.png"
        elif file_extension == ".mp4":
            icon_file = "/icons/icon-mp4.png"
        elif file_extension == ".sh":
            icon_file = "/icons/icon-sh.png"
        elif file_extension == ".deb":
            icon_file = "/icons/icon-deb.png"
        elif file_extension == ".conf":
            icon_file = "/icons/icon-conf.png"
        elif file_extension == ".ods":
            icon_file = "/icons/icon-ods.png"
        elif file_extension == ".odt":
            icon_file = "/icons/icon-odt.png"
        elif file_extension == ".css":
            icon_file = "/icons/icon-css.png"
        elif file_extension == ".php":
            icon_file = "/icons/icon-php.png"
        elif file_extension == ".js":
            icon_file = "/icons/icon-js.png"
        elif file_extension == ".java":
            icon_file = "/icons/icon-java.png"
        elif file_extension == ".log":
            icon_file = "/icons/icon-log.png"
        elif file_extension == ".svg":
            icon_file = "/icons/icon-svg.png"
        elif file_extension == ".rpm":
            icon_file = "/icons/icon-rpm.png"
        elif file_extension == ".jpeg":
            icon_file = "/icons/icon-jpeg.png"
        elif file_extension == ".py":
            icon_file = "/icons/icon-py.png"
        elif file_extension == ".db":
            icon_file = "/icons/icon-db.png"
        else:
            icon_file = "/icons/icon-file.png"

        return icon_file

    def update_foldeview(self, maincontainer, parent_folder):
        
        root_path = os.path.abspath(os.sep)
        app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        
        listoffiles = os.listdir(parent_folder)
        listoffiles.sort()
        
        col = 1
        dir_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        mainbox.set_name("folderview")
        lblhead = Gtk.Label(parent_folder.replace("/", "  >  "))
        lblhead.set_name("lblhead")
        mainbox.pack_start(lblhead, False, False, 0)

        screen_width, screen_height = screensize.get_screen_size() 

        scroll = Gtk.ScrolledWindow()
        scroll.set_size_request(screen_width/2, screen_height*0.4)        
        
        if parent_folder != root_path:
            rowbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
            imagebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            dirimage = Gtk.Image()            
            dirimage.set_from_file(app_path + "/icons/icon-up.png")
            imagebox.pack_start(dirimage, True, True, 0)
            dirlable = Gtk.Label("Go up")
            imagebox.pack_end(dirlable, True, True, 0)
            eventbox = Gtk.EventBox()
            eventbox.add(imagebox)
            eventbox.connect("button_press_event",self.on_folder_click, parent_folder, "goup", maincontainer, scroll)
            eventbox.connect("enter-notify-event", self.on_mouse_enter)
            eventbox.connect("leave-notify-event", self.on_mouse_leave)
            eventbox.set_tooltip_text("Go Up")
            rowbox.pack_start(eventbox, False, False, 50)
            col = 2

        # first directories        
        for dir_entry in listoffiles:
            fullpath = os.path.join(parent_folder, dir_entry)
            if os.path.isdir(fullpath):
                if col == 1:
                    rowbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)

                imagebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                dirimage = Gtk.Image()
                dirimage.set_from_file(app_path + "/icons/icon-folder.png")
                imagebox.pack_start(dirimage, True, True, 0)
                dirlable = Gtk.Label(dir_entry)
                dirlable.set_max_width_chars(1)
                dirlable.set_ellipsize(pango.EllipsizeMode.END)
                imagebox.pack_end(dirlable, True, True, 0)
                eventbox = Gtk.EventBox()
                eventbox.add(imagebox)                
                eventbox.connect("button_press_event",self.on_folder_click, fullpath, "dir", maincontainer, scroll)
                eventbox.connect("enter-notify-event", self.on_mouse_enter)
                eventbox.connect("leave-notify-event", self.on_mouse_leave)               
                eventbox.set_tooltip_text(dir_entry)
                rowbox.pack_start(eventbox, False, False, 50)
                
                col = col + 1
                if col == 6:
                    col = 1
                
            dir_box.pack_start(rowbox, False, False, 0)
        

        for file_entry in listoffiles:
            fullpath = os.path.join(parent_folder, file_entry)
            if os.path.isdir(fullpath) == False:
                if col == 1:
                    rowbox =Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
                
                imagebox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
                fileimage = Gtk.Image()
                fileimage.set_from_file(app_path + self.get_file_icon(fullpath))
                imagebox.pack_start(fileimage, True, True, 0)
                filelable = Gtk.Label(file_entry)
                filelable.set_max_width_chars(1)
                filelable.set_ellipsize(pango.EllipsizeMode.END)
                imagebox.pack_end(filelable, True, True, 0)
                eventbox = Gtk.EventBox()
                eventbox.add(imagebox)
                eventbox.connect("button_press_event",self.on_folder_click, fullpath, "dir", maincontainer, scroll)
                eventbox.connect("enter-notify-event", self.on_mouse_enter)
                eventbox.connect("leave-notify-event", self.on_mouse_leave)
                eventbox.set_tooltip_text(file_entry)
                rowbox.pack_start(eventbox, False, False, 50)

                col = col + 1
                if col == 6:
                    col = 1

                dir_box.pack_start(rowbox, False, False, 0)
        
        if len(listoffiles) == 0:            
            dir_box.pack_start(rowbox, False, False, 0)

        scroll.add(dir_box)
        scroll.show_all()
        mainbox.pack_start(scroll, False, False, 0)
        mainbox.show_all()
        maincontainer.add(mainbox)

    


    