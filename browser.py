#!/usr/bin/python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk','3.0')
gi.require_version('WebKit2','4.0')
from gi.repository import Gtk, Gdk, GdkPixbuf
from gi.repository import WebKit2
import os
import sys
import time
import sqlite3
import requests
from urllib.parse import urlparse
import screensize

app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
db = sqlite3.connect(app_path + "/database/history.db")
cur = db.cursor()

# Dialog for history
class HistoryDialog(Gtk.Dialog):
    def __init__(self, parent, *args, **kwargs):
        super(HistoryDialog, self).__init__(*args, **kwargs)
        Gtk.Dialog.__init__(self, "My Dialog", parent, 0)

        screen_width, screen_height = screensize.get_screen_size()        
        self.set_default_size(screen_width/2, screen_height/2)
        # Without title bar
        self.set_titlebar(None)
        self.set_decorated(False)

        # Two buttons ok and cancel
        self.add_button("Ok", Gtk.ResponseType.OK)
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        
        # List selection entry
        self.entry_path = Gtk.Entry()
        self.entry_path.set_editable(False)
        self.entry_name = Gtk.Entry()
        self.entry_name.set_editable(False)
        self.lbl_path = Gtk.Label()
        self.lbl_path.set_text("Path:")
        self.lbl_name = Gtk.Label()
        self.lbl_name.set_text("Name:")

        history_list = []
        cur.execute('''SELECT title, link FROM history''')
        # Appending to history list from sqlite cursor
        for row in cur:
            history_list.append([row[0], row[1]])
        
        # Liststore with two columns, path and nama
        self.history_liststore = Gtk.ListStore(str, str)

        # Appendig to liststore from history list
        for history_ref in history_list:
            self.history_liststore.append(list(history_ref))
        
        # A treeview with model history liststore
        self.treeview = Gtk.TreeView.new_with_model(model=self.history_liststore)

        # Setting column headers, name and location
        for i, column_title in enumerate(["Name", "Location"]):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(column_title, renderer, text=i)
            self.treeview.append_column(column)        

        # Setting up activation on single click
        self.treeview.set_activate_on_single_click(True)
        self.treeview.connect("row-activated", self.on_activate_treeview)             
        self.treeview.show_all()

        self.scrollable_treelist = Gtk.ScrolledWindow()
        self.scrollable_treelist.set_vexpand(True)
        self.scrollable_treelist.add(self.treeview)

        # Getting Dialog content area
        box = self.get_content_area()        
        # Then adding widgets to content area, box
        box.add(self.scrollable_treelist)
        box.add(self.lbl_name)
        box.add(self.entry_name)
        box.add(self.lbl_path)
        box.add(self.entry_path)

        # If there is history then selecting first row of history list
        if len(history_list) > 0:
            self.on_activate_treeview(self.treeview, 0, 0)  

        self.show_all()  

    def on_activate_treeview(self, treeview, path, column):   
        # Treeview model, list     
        model = treeview.get_model()
        # List contents to array
        tree_iter = model.get_iter(path)
        # Passing entry boxes
        self.entry_name.set_text(model[tree_iter][0])
        self.entry_path.set_text(model[tree_iter][1])

class MessageBar(Gtk.Revealer):

    def __init__(self):
        Gtk.Revealer.__init__(self)

        self.set_valign(Gtk.Align.END)

        # Main Bar
        self.bar = Gtk.Box(homogeneous=Gtk.Orientation.HORIZONTAL)
        self.bar.set_name("messagebar")
        self.add(self.bar)

        # Message Label
        self.label = Gtk.Label(label='Info')
        self.bar.pack_start(self.label, False, False, 0)       

    def close(self, widget=None):
        self.reveal(False)

    def show_info(self, message='Undefined'):        
        self.label.set_text(message)
        self.reveal(True)

    def reveal(self, reveal):
        self.set_reveal_child(reveal)

class Browser():
    def __init__(self):
        
        self.stop_reload_flag = "stop"
        self.page_loaded_flag = "true"
        self.notebook = Gtk.Notebook()
        self.notebook.set_name("browserpage")

    def create_browser(self):                

        overlay = Gtk.Overlay()
        url_bar = Gtk.Entry()
        url_bar.set_name("urlbar")        
        webview = WebKit2.WebView()           
        # Liststore for entry completion
        liststore = Gtk.ListStore(str)
        entrycompletion = Gtk.EntryCompletion()
        entrycompletion.set_model(liststore)
        entrycompletion.set_text_column(0)
        # Stop loading, image and event box
        stop_image = Gtk.Image()
        eventbox_stop = Gtk.EventBox()
        vboxmain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vboxmain.set_name("boxbrowser")

        # box for webview
        view_boxbrowser = Gtk.Box()
        screen_width, screen_height = screensize.get_screen_size() 
        webview.set_size_request(screen_width/2, screen_height*0.5)        
        webview.show()        
        view_boxbrowser.pack_start(webview, True, True, 0)
        vboxmain.pack_end(view_boxbrowser, True, True, 0)
        
        # Address bar
        address_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        backward_image = Gtk.Image()
        backward_image.set_from_file("./icons/icon-back.png")
        eventbox_back = Gtk.EventBox()
        eventbox_back.add(backward_image)               
        eventbox_back.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_back.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_back.set_tooltip_text("Go back")
        
        # Webview forwar
        forward_image = Gtk.Image()
        forward_image.set_from_file("./icons/icon-next.png")
        eventbox_next = Gtk.EventBox()
        eventbox_next.add(forward_image)
        eventbox_next.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_next.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_next.set_tooltip_text("Go forward")   

        # Stop image, as stop button
        stop_image.set_from_file("./icons/icon-stop.png")
        stop_image.show()        
        eventbox_stop.add(stop_image)        
        eventbox_stop.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_stop.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_stop.set_tooltip_text("Stop loading")     

        # Go button, load url
        go_image = Gtk.Image()
        go_image.set_from_file("./icons/icon-go.png")
        eventbox_go = Gtk.EventBox()
        eventbox_go.add(go_image)        
        eventbox_go.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_go.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_go.set_tooltip_text("Load url")   

        #entry        
        self.append_liststore(liststore)
        url_bar.set_completion(entrycompletion)
        url_bar.set_placeholder_text ("Enter address")
        url_bar.connect("activate", self.load_url, stop_image, eventbox_stop, webview)        
        
        # History, to show history dialog
        history_image = Gtk.Image()
        history_image.set_from_file("./icons/icon-history.png")
        history_image.show()        
        eventbox_history = Gtk.EventBox()
        eventbox_history.add(history_image)        
        eventbox_history.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_history.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_history.set_tooltip_text("Show history")   

        event_plus = Gtk.EventBox() # notebook tab add button        
        event_plus.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        event_plus.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        event_plus.set_tooltip_text("Open a new tab")
        image_plus = Gtk.Image()
        image_plus.set_from_file("./icons/icon-plus.png")
        event_plus.add(image_plus)

        # Add widget to address box
        address_box.add(eventbox_back)
        address_box.add(eventbox_next)
        address_box.add(eventbox_stop)        
        address_box.pack_start(url_bar, True, True,0)
        address_box.add(eventbox_go)
        address_box.add(eventbox_history)
        address_box.add(event_plus)
        
        # Address box to main box
        vboxmain.add(address_box)
        vboxmain.pack_start(view_boxbrowser, True, True, 0)    
        
        # Message bar for webview
        message_bar = MessageBar()
        overlay.add(vboxmain)
        overlay.add_overlay(message_bar)     

        # Notebook tab
        box_tab = Gtk.HBox(spacing=8)
        image_icon = Gtk.Image()
        label_title = Gtk.Label()
        label_title.set_text("New tab")
        box_tab.pack_start(image_icon, False, False, 0)
        box_tab.pack_start(label_title, False, False, 0)
        box_tab.show_all()
        overlay.show_all()
        self.notebook.append_page(overlay, box_tab)        

        webview.connect("load-failed", webview.do_load_failed)
        webview.connect("load-changed", self.on_load_changed, stop_image, eventbox_stop, message_bar, image_icon)
        webview.connect("resource_load_started", self.on_resource_load_started, message_bar)
        webview.connect('notify::title', self.change_title, label_title, webview)
        eventbox_back.connect("button_press_event", self.webview_goback, webview) 
        eventbox_next.connect("button_press_event", self.webview_goforward, webview)
        eventbox_stop.connect("button_press_event", self.webview_stop_reload, stop_image, webview, eventbox_stop, message_bar)
        eventbox_go.connect("button_press_event", self.on_go_click, url_bar, stop_image, eventbox_stop, webview)
        eventbox_history.connect("button_press_event", self.show_history_page, stop_image, eventbox_stop, webview, url_bar)        
        event_plus.connect("button_press_event", self.create_page)

        self.notebook.set_current_page(0)

        return self.notebook

    def create_page(self, widget, event):

        overlay = Gtk.Overlay()
        # Address bar
        url_bar = Gtk.Entry()
        url_bar.set_name("urlbar")
        webview = WebKit2.WebView()      
        # History list for entry completion     
        liststore = Gtk.ListStore(str)
        entrycompletion = Gtk.EntryCompletion()
        entrycompletion.set_model(liststore)
        entrycompletion.set_text_column(0)
        # Stop loading web page and its event box
        stop_image = Gtk.Image()
        eventbox_stop = Gtk.EventBox()
        vboxmain = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vboxmain.set_name("boxbrowser")

        view_boxbrowser = Gtk.Box()
        screen_width, screen_height = screensize.get_screen_size() 
        webview.set_size_request(screen_width/2, screen_height*0.5)        
        webview.show()        
        view_boxbrowser.pack_start(webview, True, True, 0)
        vboxmain.pack_end(view_boxbrowser, True, True, 0)
        
        # Address box 
        address_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        # web page backward button
        backward_image = Gtk.Image()
        backward_image.set_from_file(app_path + "/icons/icon-back.png")
        eventbox_back = Gtk.EventBox()
        eventbox_back.add(backward_image)          
        eventbox_back.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_back.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_back.set_tooltip_text("Go back")

        # Webpage forward button
        forward_image = Gtk.Image()
        forward_image.set_from_file(app_path + "/icons/icon-next.png")
        eventbox_next = Gtk.EventBox()
        eventbox_next.add(forward_image)
        eventbox_next.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_next.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_next.set_tooltip_text("Go forward")   
        
        # Stop loading page, button
        stop_image.set_from_file(app_path + "/icons/icon-stop.png")
        stop_image.show()        
        eventbox_stop.add(stop_image) 
        eventbox_stop.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_stop.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_stop.set_tooltip_text("Stop loading")     
        
        # Go button, load url
        go_image = Gtk.Image()
        go_image.set_from_file(app_path + "/icons/icon-go.png")
        eventbox_go = Gtk.EventBox()
        eventbox_go.add(go_image)
        eventbox_go.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_go.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_go.set_tooltip_text("Load url")           
        
        #entry        
        self.append_liststore(liststore)
        url_bar.set_completion(entrycompletion)        
        url_bar.set_placeholder_text ("Enter address")
        url_bar.connect("activate", self.load_url, stop_image, eventbox_stop, webview)        
        
        # History button, to show history dialog
        history_image = Gtk.Image()
        history_image.set_from_file(app_path + "/icons/icon-history.png")
        history_image.show()        
        eventbox_history = Gtk.EventBox()
        eventbox_history.add(history_image)
        eventbox_history.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_history.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        eventbox_history.set_tooltip_text("Show history")   

        event_plus = Gtk.EventBox() # notebook tab close button
        event_plus.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        event_plus.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        event_plus.set_tooltip_text("Open a new tab")
        image_plus = Gtk.Image()
        image_plus.set_from_file(app_path + "/icons/icon-plus.png")
        event_plus.add(image_plus)        

        # Adding addressbox to its widgets
        address_box.add(eventbox_back)
        address_box.add(eventbox_next)
        address_box.add(eventbox_stop)        
        address_box.pack_start(url_bar, True, True,0)
        address_box.add(eventbox_go)
        address_box.add(eventbox_history)
        address_box.add(event_plus)   

        # Address box to main box
        vboxmain.add(address_box)
        # webvew to main box
        vboxmain.pack_start(view_boxbrowser, True, True, 0)    

        message_bar = MessageBar()
        overlay.add(vboxmain)
        overlay.add_overlay(message_bar)    
        
        # Notebokk tab box
        box_tab = Gtk.HBox(spacing=8)
        close_image = Gtk.Image()
        close_image.set_from_file(app_path + "/icons/icon-close.png")
        image_icon = Gtk.Image()
        eventbox_close = Gtk.EventBox()
        eventbox_close.set_name("eventboxclose")
        eventbox_close.add(close_image)
        eventbox_close.connect("enter-notify-event", self.on_mouse_enter_button_icon)
        eventbox_close.connect("leave-notify-event", self.on_mouse_leave_button_icon)
        label_title = Gtk.Label()
        label_title.set_text("New tab")
        box_tab.pack_start(image_icon, False, False, 0)
        box_tab.pack_start(label_title, False, False, 0)
        box_tab.pack_start(eventbox_close, False, False, 0)
        box_tab.set_name("booktab")

        box_tab.show_all()
        overlay.show_all()
        self.notebook.append_page(overlay, box_tab)
        
        webview.connect("load-failed", webview.do_load_failed)
        webview.connect("load-changed", self.on_load_changed, stop_image, eventbox_stop, message_bar, image_icon )
        webview.connect("resource_load_started", self.on_resource_load_started, message_bar)
        webview.connect('notify::title', self.change_title, label_title, webview)
        eventbox_back.connect("button_press_event", self.webview_goback, webview) 
        eventbox_next.connect("button_press_event", self.webview_goforward, webview)
        eventbox_stop.connect("button_press_event", self.webview_stop_reload, stop_image, webview, eventbox_stop, message_bar)
        eventbox_go.connect("button_press_event", self.on_go_click, url_bar, stop_image, eventbox_stop, webview)
        eventbox_history.connect("button_press_event", self.show_history_page, stop_image, eventbox_stop, webview, url_bar)
        event_plus.connect("button_press_event", self.create_page)        
        eventbox_close.connect("button_press_event", self.close_tab) 

        # Show page newly added
        self.notebook.set_current_page(self.notebook.get_n_pages() - 1)
        self.notebook.show_all()

    def close_tab(self, widget, event):
        
            page = self.notebook.get_current_page()
            self.notebook.remove_page(page)

    def load_url(self, widget, stop_image, eventbox_stop, webview):
        url = widget.get_text()
        if len(url.strip()) != 0:
            app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            stop_image.set_from_file(app_path + "/icons/icon-stop.png")
            self.stop_reload_flag = "stop"
            eventbox_stop.set_tooltip_text("Stop loading")
            
            if not "://" in url:
                url = "http://"+url
            webview.load_uri(url)
            widget.set_text(url)
            self.page_loaded_flag = "false"    
    
    def on_go_click(self, w, e, url_bar, stop_image, eventbox_stop, webview):
        url = url_bar.get_text()
        if len(url.strip()) != 0:
            app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            stop_image.set_from_file(app_path + "/icons/icon-stop.png")
            self.stop_reload_flag = "stop"
            eventbox_stop.set_tooltip_text("Stop loading")
            
            if not "://" in url:
                url = "http://"+url
            webview.load_uri(url)
            url_bar.set_text(url)
            self.page_loaded_flag = "false"

    def on_resource_load_started(self, web_view, resource, request, message_bar):

        if self.page_loaded_flag == "false":
            message_bar.show_info("Transfering data from " + web_view.get_uri())
        else:
            message_bar.close()    

    def on_load_changed(self, webview, event, stop_image, eventbox_stop, message_bar, image_icon):

        if event == WebKit2.LoadEvent.FINISHED:
            resource = webview.get_main_resource()
            resource.get_data(None, self._get_response_data_finish, None)
            try:
                tittle = webview.get_title()          
                app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
                stop_image.set_from_file(app_path + "/icons/icon-reload.png")
                self.stop_reload_flag = "reload"
                eventbox_stop.set_tooltip_text("Reload")
                self.page_loaded_flag = "true"
                message_bar.close()                
                if tittle != None:
                    self.write_history(resource.get_uri(), tittle)      
            except:
                app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
                stop_image.set_from_file(app_path + "/icons/icon-reload.png")
                self.stop_reload_flag = "reload"
                eventbox_stop.set_tooltip_text("Reload")
                self.page_loaded_flag = "true"
                message_bar.close()

            parsed_uri = urlparse(resource.get_uri())
            root = '{uri.netloc}/'.format(uri=parsed_uri)
            icon_path = "http://" +  root + "favicon.ico"
            try:
                r = requests.get(icon_path, allow_redirects=True)
                open(app_path + '/icons/favicon.ico', 'wb').write(r.content)   
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(app_path + '/icons/favicon.ico', width=16, height=16, preserve_aspect_ratio=True)
                image_icon.set_from_pixbuf(pixbuf)
            except:
                pass
            
    def  _get_response_data_finish(self, resource, result, user_data=None):
        self.html_response = resource.get_data_finish(result)

    def change_title(self, widget, frame, lbl, webview):
        title = webview.get_title()
        if len(title) > 5:
            title = title[:4] + "..."
        lbl.set_text(title)

    def on_mouse_enter_button_icon(self, w, e):
        w.get_window().set_cursor(Gdk.Cursor(Gdk.CursorType.HAND2))
        w.get_style_context().add_class("refresh-button-hover")

    def on_mouse_leave_button_icon(self, w, e):
        w.get_window().set_cursor(None)
        w.get_style_context().remove_class("refresh-button-hover")

    def webview_goback(self, w, e, webview):
        webview.go_back()

    def webview_goforward(self, w, e, webview):
        webview.go_forward()

    def webview_stop_reload(self, w, e, stop_image, webview, eventbox_stop, message_bar):
        if self.stop_reload_flag == "stop":
            webview.stop_loading()
            app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            stop_image.set_from_file(app_path + "/icons/icon-reload.png")
            self.stop_reload_flag = "reload"
            eventbox_stop.set_tooltip_text("Reload")
            self.page_loaded_flag = "true"
            message_bar.close()
        else:
            webview.reload()
            app_path = os.path.abspath(os.path.dirname(sys.argv[0]))
            stop_image.set_from_file(app_path + "/icons/icon-stop.png")
            self.stop_reload_flag = "reload"
            eventbox_stop.set_tooltip_text("Stop loading")
            self.page_loaded_flag = "false"

    def show_history_page(self, widget, e, stop_image, eventbox_stop, webview, url_bar):
        dialog = HistoryDialog(self) 
        response = dialog.run()  
        entry_text = dialog.entry_path.get_text().strip()
        if response == Gtk.ResponseType.OK:  
            if len(entry_text) != 0:
                url_bar.set_text(entry_text)
                self.load_url(url_bar, stop_image, eventbox_stop, webview)  
        dialog.destroy()
        
    def append_liststore(self, liststore):
        liststore.clear()
        cur.execute('''SELECT root FROM history''')
        for row in cur:
            liststore.append([row[0]])

    def write_history(self, url, title):
        # checking already listed in histor
        do_write = True
        cur.execute('''SELECT link FROM history''')
        for row in cur:
            if url in row[0]:
                do_write = False
                break
            time.sleep(0.02)

        if do_write:            
            # finding root url
            parsed_uri = urlparse(url)
            domain = '{uri.netloc}/'.format(uri=parsed_uri)
            root = domain.replace('www.', '')

            cur.execute('''INSERT INTO history(root, link, title) VALUES(?,?,?)''', (root,url,title))
            db.commit()
