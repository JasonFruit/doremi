from __future__ import print_function

import codecs
from doremi.doremi_parser import *

import gtk, pango

notes = ["do", "re", "mi", "fa", "sol", "la", "ti"]

chromatics = {"do": (None, "di"),
              "re": ("ra", "ri"),
              "mi": ("me", None),
              "fa": (None, "fi"),
              "sol": ("se", "si"),
              "la": ("le", "li"),
              "ti": ("te", None)}

durations = [u"\U0001D15D",
             u"\U0001D15E",
             u"\U0001D15F",
             u"\U0001D160",
             u"\U0001D161"]

barlines = [u"\U0001D106",
            u"\U0001D107",
            u"\U0001D101",
            u"\U0001D102"]

endings = ["{1}", "{2}"]

def toolbar_separator():
    sep = gtk.Label("")
    sep.set_size_request(10, 0)
    return sep

class MainWindow(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title("Doremi Editor")
        self.connect("destroy", gtk.main_quit)

        self.main_vbox = gtk.VBox()
        self.add(self.main_vbox)

        self.notation_buttons = self.build_notation_bar()
        self.main_vbox.pack_start(self.notation_buttons, False)
        
    def build_notation_bar(self):
        
        notation_buttons = gtk.HBox()
        
        for note in notes:
            btn = gtk.Button(note)
            btn.set_size_request(50, 50)
            notation_buttons.pack_start(btn, False)

        sep = toolbar_separator()
        notation_buttons.pack_start(sep, False)
        
        for duration in durations:
            btn = gtk.Button(duration)
            lbl = btn.child
            lbl.modify_font(pango.FontDescription("24"))
            btn.set_size_request(50, 50)
            notation_buttons.pack_start(btn, False)

        sep = toolbar_separator()
        notation_buttons.pack_start(sep, False)
        
        self.sharp_btn = gtk.Button(u"\u266F")
        self.sharp_btn.child.modify_font(pango.FontDescription("24"))
        self.sharp_btn.set_size_request(50, 50)
        notation_buttons.pack_start(self.sharp_btn, False)

        self.natural_btn = gtk.Button(u"\u266E")
        self.natural_btn.child.modify_font(pango.FontDescription("24"))
        self.natural_btn.set_size_request(50, 50)
        notation_buttons.pack_start(self.natural_btn, False)

        self.flat_btn = gtk.Button(u"\u266D")
        self.flat_btn.child.modify_font(pango.FontDescription("24"))
        self.flat_btn.set_size_request(50, 50)
        notation_buttons.pack_start(self.flat_btn, False)

        sep = toolbar_separator()
        notation_buttons.pack_start(sep, False)
        
        for barline in barlines:
            btn = gtk.Button(barline)
            lbl = btn.child
            lbl.modify_font(pango.FontDescription("24"))
            btn.set_size_request(50, 50)
            notation_buttons.pack_start(btn, False)
            
        for ending in endings:
            btn = gtk.Button(ending)
            lbl = btn.child
            btn.set_size_request(50, 50)
            notation_buttons.pack_start(btn, False)

        return notation_buttons

    def run(self):
        self.show_all()
        gtk.main()

if __name__ == "__main__":
    mw = MainWindow()
    mw.run()
