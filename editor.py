from __future__ import print_function

import codecs
import gtk, pango

from doremi.doremi_parser import *
from doremi_canvas import DoremiCanvas

notes = ["do", "re", "mi", "fa", "sol", "la", "ti"]

chromatics = {"do": (None, "di"),
              "re": ("ra", "ri"),
              "mi": ("me", None),
              "fa": (None, "fi"),
              "sol": ("se", "si"),
              "la": ("le", "li"),
              "ti": ("te", None)}

durations = [("1", u"\U0001D15D"),
             ("2", u"\U0001D15E"),
             ("4", u"\U0001D15F"),
             ("8", u"\U0001D160"),
             ("16", u"\U0001D161")]

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
    def __init__(self, tune=None):
        gtk.Window.__init__(self)
        self.set_title("Doremi Editor")
        self.connect("destroy", gtk.main_quit)
        self.connect("key-press-event", self.keypress_handler)
        self.tune = tune
        
        self.main_vbox = gtk.VBox()
        self.add(self.main_vbox)

        self.notation_buttons = self.build_notation_bar()
        self.main_vbox.pack_start(self.notation_buttons, False)

        self.scroll = gtk.ScrolledWindow()
        self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.voice_vbx = gtk.VBox()

        self.scroll.add_with_viewport(self.voice_vbx)

        self.canvases = [DoremiCanvas(tune,
                                      voice.name)
                         for voice in tune]

        for canvas in self.canvases:
            self.voice_vbx.pack_start(canvas, False)

        self.canvases[0].toggle_focus()

        self.main_vbox.pack_start(self.scroll, True)
        self.duration = "4"

    def redraw(self):
        for c in self.canvases:
            c.draw()

    def save_file(self):
        print(self.tune.to_lilypond("A major",
                                    0,
                                    "aikin",
                                    Lyric()))

    def focused_canvas(self):
        return [c for c in self.canvases
                if c.focus][0]

    def prev_voice(self):
        for i in range(len(self.canvases)):
            c = self.canvases[i]
            if c.focus:
                c.toggle_focus()
                self.canvases[i - 1].toggle_focus()
                self.redraw()
                break

    def next_voice(self):
        for i in range(len(self.canvases)):
            c = self.canvases[i]
            if c.focus:
                c.toggle_focus()
                if i < len(self.canvases) - 1:
                    self.canvases[i + 1].toggle_focus()
                else:
                    self.canvases[0].toggle_focus()
                self.redraw()
                break

    def make_note(self, pitch="r"):
        index = self.focused_canvas().active_index()

        # use the octave of the most recent note, otherwise default to 0
        while True:
            try:
                octave = self.focused_canvas().voice[index].octave
                break
            except AttributeError:
                index -= 1
            except IndexError:
                octave = 0
                break
                    
        return Note(pitch=pitch,
                    duration=self.duration,
                    octave=octave)

    def up_octave(self):
        try:
            o = self.focused_canvas().active_item().octave
            self.focused_canvas().active_item().octave += 1
            self.focused_canvas().draw()
        except AttributeError, ValueError:
            pass

    def down_octave(self):
        try:
            o = self.focused_canvas().active_item().octave
            self.focused_canvas().active_item().octave -= 1
            self.focused_canvas().draw()
        except AttributeError, ValueError:
            pass

    def tie(self):
        try:
            item = self.focused_canvas().active_item()
            
            if "tie" in item.modifiers:
                item.modifiers.remove("tie")
            else:
                item.modifiers.append("tie")
                
            self.focused_canvas().draw()
        except AttributeError, ValueError:
            pass

    def toggle_slur(self):
        try:
            item = self.focused_canvas().active_item()
            voice = self.focused_canvas().voice
            next_index = self.focused_canvas().active_index() + 1
            next = voice[next_index]

            if "slur" in item.modifiers:

                item.modifiers.remove("slur")

                for note in voice[next_index:]:
                    try:
                        if "slur" in note.modifiers:
                            break
                        elif "end slur" in note.modifiers:
                            note.modifiers.remove("end slur")
                            break
                    except: # we should keep on no matter what
                        pass

            else:
                item.modifiers.append("slur")

            self.focused_canvas().draw()

        except AttributeError, ValueError:
            pass

    def toggle_end_slur(self):
        try:
            item = self.focused_canvas().active_item()
            voice = self.focused_canvas().voice
            next = voice[self.focused_canvas().active_index() + 1]

            if "end slur" in item.modifiers:
                item.modifiers.remove("end slur")
            else:
                item.modifiers.append("end slur")

            self.focused_canvas().draw()
        except AttributeError, ValueError:
            pass

    def toggle_dot(self):
        try:
            item = self.focused_canvas().active_item()
            if item.duration[-1] == ".":
                item.duration = item.duration.replace(".", "")
            else:
                item.duration = "%s." % item.duration
            self.focused_canvas().draw()
        except AttributeError, ValueError:
            pass
    
    def keypress_handler(self, w, e):
        try:
            v = gtk.gdk.keyval_name(e.keyval)
        except ValueError:
            return False

        if v == "Up":
            self.prev_voice()
        elif v == "Down":
            self.next_voice()
        elif v == "Left":
            self.focused_canvas().move_prev()
        elif v == "Right":
            self.focused_canvas().move_next()
        elif v == "Delete":
            self.focused_canvas().delete_note()
        elif v == "BackSpace":
            self.focused_canvas().move_prev()
            self.focused_canvas().delete_note()
        elif v in "drmfslt":
            # C-s saves the file
            if v == "s" and e.state == gtk.gdk.CONTROL_MASK:
                # TODO: make this output Doremi code to a file
                self.save_file()
            else:
                pitch=[note for note in notes
                           if note[0] == v][0]
                self.focused_canvas().insert_note(self.make_note(pitch))
        elif v == "x":
            self.focused_canvas().insert_note(self.make_note())
        elif v in "12486":
            if v == "6":
                self.duration = "16"
            else:
                self.duration = v
        elif v == "plus":
            self.up_octave()
        elif v == "minus":
            self.down_octave()
        elif v == "underscore":
            pass # TODO: flatten
        elif v == "comma":
            self.tie()
        elif v == "parenleft":
            self.toggle_slur()
        elif v == "parenright":
            self.toggle_end_slur()
        elif v == "period":
            self.toggle_dot()
        else:
            print(v)
            return False

        return True
                
    def build_notation_bar(self):
        
        notation_buttons = gtk.HBox()
        
        for note in notes:
            btn = gtk.Button(note)
            btn.set_size_request(50, 50)
            notation_buttons.pack_start(btn, False)

        sep = toolbar_separator()
        notation_buttons.pack_start(sep, False)
        
        for duration in durations:
            btn = gtk.Button(duration[1])
            btn.duration = duration[0]
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
        self.maximize()
        gtk.main()

if __name__ == "__main__":
    import sys
    dp = DoremiParser(sys.argv[1])
    tune = dp.convert()
    mw = MainWindow(tune)
    mw.run()
